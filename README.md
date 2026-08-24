# Barbakaï OS

Système d’exploitation personnel de **Barbakaï**.  
Fait pour jouer, pour le PC serveur, et pour remplacer Windows au quotidien.  
**Pas de clé d’activation. Jamais.**

Base : [Bazzite](https://bazzite.gg) (Fedora Atomic / Universal Blue) — Steam, Proton, GameMode, MangoHud déjà inclus.  
Bureau : KDE Plasma. Image technique : `ghcr.io/gouverneurzqc/nexusos:latest`.

```
Utilisateur : barbakai
Mot de passe temporaire : Thegamecontrol!
Nom de machine : barbakai
```

Change le mot de passe après la première connexion (`passwd`). Le dépôt GitHub est public.

---

## Aperçu dans VirtualBox (Windows)

Les réglages VM à la main, c’est fini. Dans PowerShell, à la racine du dépôt :

```powershell
.\preview-barbakai.ps1
```

Le script trouve l’ISO, crée une VM **Barbakai** (EFI, 8 Go RAM, 4 CPU) et la lance.

Si l’ISO n’est pas encore là : GitHub → onglet **Actions** → lancer **Build container image**, puis **Build disk images** (amd64). Télécharge l’artifact `artifact-anaconda-iso`, dézippe-le dans le dépôt, relance le script.

---

## Installer sur une vraie machine

1. Télécharge l’ISO (artifact GitHub `anaconda-iso`).
2. Grave-la avec [Ventoy](https://www.ventoy.net/) ou [Fedora Media Writer](https://fedoraproject.org/os/download) / Rufus (mode DD).
3. Boot le PC (tour gaming ou serveur) sur la clé.
4. L’installateur demande surtout **le disque**. Le compte `barbakai` est déjà créé.
5. Redémarre, connecte-toi : `barbakai` / `Thegamecontrol!`.

Même image sur les deux machines. Les mises à jour :

```bash
sudo bootc upgrade
sudo reboot
```

Sur une machine déjà en Bazzite / Fedora bootc :

```bash
sudo bootc switch ghcr.io/gouverneurzqc/nexusos:latest
sudo reboot
```

---

## Ce qui est à ton image

- Nom **Barbakaï** partout : écran de connexion, fond d’écran, boot, terminal, `os-release`
- Sigle **B** obsidienne, cyan / magenta, anneau orbital
- Wallpaper « salle des machines » sous nébuleuse — serveur + gaming
- Slogan **The Game Control**
- Compte `barbakai` en administrateur (`wheel`)
- Commande `barbakai-info`

Les visuels sont dans `system_files/usr/share/`. Pour les régénérer après un nouveau dessin : `python tools/compose_branding.py`.

---

## Construire l’image (GitHub)

Windows ne construit pas l’ISO localement (il faut Podman + bootc). Le dépôt le fait tout seul :

| Workflow | Résultat |
|---|---|
| **Build container image** | Image `ghcr.io/gouverneurzqc/nexusos:latest` |
| **Build disk images** | ISO d’installation + disque QCOW2 |

Détail technique (template Universal Blue, Justfile, cosign) : [docs/BUILD.md](docs/BUILD.md).
