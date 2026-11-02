require("dotenv").config({ path: "../.env" });
const {
  Client,
  GatewayIntentBits,
  EmbedBuilder,
  REST,
  Routes,
  SlashCommandBuilder,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  PermissionFlagsBits,
} = require("discord.js");

const token = process.env.GESTION_BOT_TOKEN;
const appId = process.env.GESTION_CLIENT_ID;
const owners = (process.env.OWNER_IDS || "")
  .split(",")
  .map((x) => x.trim())
  .filter(Boolean);
const img = process.env.NETO_IMAGE_URL || "";

if (!token || !appId) {
  console.error("GESTION_BOT_TOKEN et GESTION_CLIENT_ID manquants");
  process.exit(1);
}

const bot = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

const defs = [
  ["ping", "Latence du bot"],
  ["serverinfo", "Informations du serveur"],
  ["userinfo", "Informations sur un membre"],
  ["say", "Faire parler le bot"],
  ["clear", "Supprimer des messages"],
  ["kick", "Expulser un membre"],
  ["ban", "Bannir un membre"],
  ["unban", "Débannir un membre"],
  ["timeout", "Timeout un membre"],
  ["untimeout", "Retirer un timeout"],
  ["lock", "Verrouiller un salon"],
  ["unlock", "Déverrouiller un salon"],
  ["slowmode", "Définir le slowmode"],
  ["announce", "Poster une annonce"],
  ["poll", "Créer un sondage"],
  ["roleadd", "Ajouter un rôle"],
  ["roleremove", "Retirer un rôle"],
  ["nick", "Changer le surnom"],
  ["ticketpanel", "Panneau de ticket"],
  ["botinfo", "Informations du bot"],
  ["help", "Afficher l’aide"],
  ["maintenance", "Annonce de maintenance"],
  ["servericon", "Icône du serveur"],
  ["membercount", "Nombre de membres"],
];

const cmds = defs.map(([name, description]) =>
  new SlashCommandBuilder().setName(name).setDescription(description)
);

function emb(title, description) {
  const e = new EmbedBuilder()
    .setColor(0xd4af37)
    .setTitle(title)
    .setDescription(description)
    .setTimestamp()
    .setFooter({ text: "NETO • Gestion" });

  if (img.startsWith("https://") && !img.includes("example.com")) {
    e.setImage(img);
  }

  return e;
}

const owner = (id) => owners.includes(id);

bot.once("ready", async () => {
  console.log("Gestion NETO connecté", bot.user.tag);

  try {
    await new REST({ version: "10" })
      .setToken(token)
      .put(Routes.applicationCommands(appId), { body: cmds.map((c) => c.toJSON()) });
  } catch (error) {
    console.error("Erreur d’enregistrement des commandes:", error.message);
  }

  await bot.user.setActivity({ name: "/help • NETO", type: 2 });
});

bot.on("interactionCreate", async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const { commandName } = interaction;
  const adminOnly = [
    "say",
    "clear",
    "kick",
    "ban",
    "unban",
    "timeout",
    "untimeout",
    "lock",
    "unlock",
    "slowmode",
    "announce",
    "roleadd",
    "roleremove",
    "nick",
    "ticketpanel",
    "maintenance",
  ];

  if (adminOnly.includes(commandName) && !owner(interaction.user.id)) {
    await interaction.reply({ content: "⛔ Tu n’as pas la permission.", ephemeral: true });
    return;
  }

  try {
    switch (commandName) {
      case "ping":
        return interaction.reply({ embeds: [emb("🏓 Pong", `Latence : ${bot.ws.ping} ms`)] });

      case "serverinfo":
        return interaction.reply({
          embeds: [
            emb(
              interaction.guild.name,
              `ID : ${interaction.guild.id}\nMembres : ${interaction.guild.memberCount}\nSalons : ${interaction.guild.channels.cache.size}\nRôles : ${interaction.guild.roles.cache.size}`
            ),
          ],
        });

      case "userinfo": {
        const member = interaction.options.getMember("membre");
        if (!member) {
          return interaction.reply({ content: "Membre introuvable.", ephemeral: true });
        }
        return interaction.reply({
          embeds: [
            emb(
              `👤 ${member.user.tag}`,
              `ID : ${member.user.id}\nBot : ${member.user.bot ? "Oui" : "Non"}\nCompte créé : <t:${Math.floor(member.user.createdTimestamp / 1000)}:F>`
            ),
          ],
        });
      }

      case "say": {
        const text = interaction.options.getString("texte") || "Message NETO";
        await interaction.channel.send(text);
        return interaction.reply({ content: "✅ Message envoyé.", ephemeral: true });
      }

      case "clear": {
        const count = interaction.options.getInteger("nombre") || 10;
        const del = await interaction.channel.bulkDelete(Math.min(100, Math.max(1, count)), true);
        return interaction.reply({ content: `${del.size} messages supprimés.`, ephemeral: true });
      }

      case "kick": {
        const member = interaction.options.getMember("membre");
        if (!member) return interaction.reply({ content: "Membre introuvable.", ephemeral: true });
        await member.kick();
        return interaction.reply({ content: `✅ ${member.user.tag} a été expulsé.`, ephemeral: true });
      }

      case "ban": {
        const member = interaction.options.getMember("membre");
        if (!member) return interaction.reply({ content: "Membre introuvable.", ephemeral: true });
        await member.ban();
        return interaction.reply({ content: `✅ ${member.user.tag} a été banni.`, ephemeral: true });
      }

      case "unban": {
        const id = interaction.options.getString("id");
        await interaction.guild.members.unban(id);
        return interaction.reply({ content: "✅ Membre débanni.", ephemeral: true });
      }

      case "timeout": {
        const member = interaction.options.getMember("membre");
        const minutes = interaction.options.getInteger("minutes") || 5;
        if (!member) return interaction.reply({ content: "Membre introuvable.", ephemeral: true });
        await member.timeout(minutes * 60000);
        return interaction.reply({ content: `✅ Timeout appliqué à ${member.user.tag}.`, ephemeral: true });
      }

      case "untimeout": {
        const member = interaction.options.getMember("membre");
        if (!member) return interaction.reply({ content: "Membre introuvable.", ephemeral: true });
        await member.timeout(null);
        return interaction.reply({ content: `✅ Timeout retiré pour ${member.user.tag}.`, ephemeral: true });
      }

      case "lock": {
        await interaction.channel.permissionOverwrites.edit(interaction.guild.roles.everyone, {
          SendMessages: false,
        });
        return interaction.reply({ content: "🔒 Salon verrouillé.", ephemeral: true });
      }

      case "unlock": {
        await interaction.channel.permissionOverwrites.edit(interaction.guild.roles.everyone, {
          SendMessages: null,
        });
        return interaction.reply({ content: "🔓 Salon déverrouillé.", ephemeral: true });
      }

      case "slowmode": {
        const sec = interaction.options.getInteger("secondes") || 0;
        await interaction.channel.setRateLimitPerUser(sec);
        return interaction.reply({ content: `✅ Slowmode défini à ${sec} secondes.`, ephemeral: true });
      }

      case "announce": {
        const text = interaction.options.getString("texte") || "Annonce NETO";
        return interaction.reply({ embeds: [emb("📢 Annonce", text)] });
      }

      case "poll": {
        const question = interaction.options.getString("question") || "Votre avis ?";
        const msg = await interaction.channel.send({ embeds: [emb("📊 Sondage", question)] });
        await msg.react("👍");
        await msg.react("👎");
        return interaction.reply({ content: "✅ Sondage publié.", ephemeral: true });
      }

      case "roleadd": {
        const role = interaction.options.getRole("role");
        const member = interaction.options.getMember("membre");
        await member.roles.add(role);
        return interaction.reply({ content: `✅ Rôle ${role.name} ajouté.`, ephemeral: true });
      }

      case "roleremove": {
        const role = interaction.options.getRole("role");
        const member = interaction.options.getMember("membre");
        await member.roles.remove(role);
        return interaction.reply({ content: `✅ Rôle ${role.name} retiré.`, ephemeral: true });
      }

      case "nick": {
        const member = interaction.options.getMember("membre");
        const nom = interaction.options.getString("nom") || "Membre";
        await member.setNickname(nom);
        return interaction.reply({ content: `✅ Surnom changé pour ${member.user.tag}.`, ephemeral: true });
      }

      case "ticketpanel": {
        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setCustomId("ticket-open")
            .setLabel("Ouvrir un ticket")
            .setStyle(ButtonStyle.Primary)
        );
        return interaction.reply({
          embeds: [emb("🎫 Support NETO", "Cliquez sur le bouton pour ouvrir un ticket.")],
          components: [row],
        });
      }

      case "botinfo":
        return interaction.reply({
          embeds: [
            emb(
              "🤖 Gestion NETO",
              `ID : ${bot.user.id}\nDiscord.js : ${require("discord.js").version}\nServeurs : ${bot.guilds.cache.size}\nLatence : ${bot.ws.ping} ms`
            ),
          ],
        });

      case "help":
        return interaction.reply({
          embeds: [emb("Commandes NETO", defs.map(([a, b]) => `/${a} • ${b}`).join("\n"))],
          ephemeral: true,
        });

      case "maintenance": {
        const text = interaction.options.getString("message") || "Maintenance en cours";
        return interaction.reply({ embeds: [emb("🛠️ Maintenance", text)] });
      }

      case "servericon":
        return interaction.reply({
          embeds: [emb("Icône du serveur", interaction.guild.iconURL({ size: 1024 }) || "Aucune icône")],
        });

      case "membercount":
        return interaction.reply({ embeds: [emb("👥 Membres", `${interaction.guild.memberCount} membres`)] });

      default:
        return interaction.reply({ content: "Commande inconnue.", ephemeral: true });
    }
  } catch (error) {
    console.error(error);
    const message = "Erreur : vérifie les permissions, le rôle du bot et les options.";
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp({ content: message, ephemeral: true }).catch(() => {});
    } else {
      await interaction.reply({ content: message, ephemeral: true }).catch(() => {});
    }
  }
});

bot.on("interactionCreate", async (interaction) => {
  if (!interaction.isButton() || interaction.customId !== "ticket-open") return;

  try {
    const channel = await interaction.guild.channels.create({
      name: `ticket-${interaction.user.username}`.toLowerCase().replace(/[^a-z0-9-]/g, "").slice(0, 90),
      type: 0,
      permissionOverwrites: [
        { id: interaction.guild.id, deny: ["ViewChannel"] },
        { id: interaction.user.id, allow: ["ViewChannel", "SendMessages", "ReadMessageHistory"] },
        { id: bot.user.id, allow: ["ViewChannel", "SendMessages", "ManageChannels"] },
      ],
    });

    await channel.send(`Ticket ouvert par ${interaction.user}`);
    await interaction.reply({ content: `Ticket créé : ${channel}`, ephemeral: true });
  } catch (error) {
    console.error(error);
    await interaction.reply({ content: "Impossible de créer le ticket.", ephemeral: true }).catch(() => {});
  }
});

bot.login(token);

