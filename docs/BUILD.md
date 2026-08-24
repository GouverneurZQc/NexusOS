# Construire l’image Barbakaï

Le dépôt est un [image-template](https://github.com/ublue-os/image-template) Universal Blue.

- Image de base : `ghcr.io/ublue-os/bazzite:stable` (`Containerfile`)
- Recettes : `Justfile`
- Personnalisation : `build_files/build.sh` + `system_files/`
- Disques / ISO : `disk_config/` + workflow `build-disk.yml`

## Sur GitHub (recommandé)

1. Pousse sur `main`
2. Actions → **Build container image**
3. Actions → **Build disk images** (platform `amd64`)
4. Télécharge `artifact-anaconda-iso` et/ou `artifact-qcow2`

L’image publiée : `ghcr.io/gouverneurzqc/nexusos:latest`

## En local (Linux avec Podman)

```bash
just build
just build-iso
just run-vm-iso
```

## Cosign

Les builds GitHub signent l’image si le secret `SIGNING_SECRET` contient `cosign.key`. Voir le README du template [ublue-os/image-template](https://github.com/ublue-os/image-template).
