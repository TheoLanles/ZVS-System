# API de Streaming Vidéo HLS avec Flask

Ce projet propose une API simple pour convertir des vidéos MP4 en HLS (HTTP Live Streaming) et les diffuser via Flask.

## Prérequis

- Python 3.x
- [ffmpeg](https://ffmpeg.org/) installé et accessible dans le PATH
- Dépendances Python :
  ```bash
  pip install flask
  ```

## Lancer le serveur

```bash
python app.py
```

## Endpoints

### 1. Upload d'une vidéo MP4 et conversion en HLS

**POST** `/upload`

- Form-data :
  - `file` : fichier MP4 à uploader

**Exemple curl :**
```bash
curl -X POST -F "file=@/chemin/vers/video.mp4" http://localhost:5000/upload
```

**Réponse :**
```json
{
  "hls_url": "/hls/video1/index.m3u8"
}
```

À chaque upload, le chemin HLS sera `/hls/videoN/index.m3u8` où `N` est le numéro de la vidéo (1, 2, 3, ...).

### 2. Lister les vidéos disponibles

**GET** `/videos`

Retourne la liste des vidéos disponibles avec :
- `id` : identifiant (ex: video1)
- `title` : titre (ex: Video 1)
- `hls_url` : URL complète de la playlist HLS
- `preview_url` : URL de l'image de preview (ou null si absente)

**Exemple curl :**
```bash
curl http://localhost:5000/videos
```

**Exemple de réponse :**
```json
[
  {
    "id": "video1",
    "title": "Video 1",
    "hls_url": "http://localhost:5000/hls/video1/index.m3u8",
    "preview_url": "http://localhost:5000/hls/video1/preview.jpg"
  },
  {
    "id": "video2",
    "title": "Video 2",
    "hls_url": "http://localhost:5000/hls/video2/index.m3u8",
    "preview_url": "http://localhost:5000/hls/video2/preview.jpg"
  }
]
```

### 3. Accès au flux HLS

**GET** `/hls/videoN/index.m3u8`

- Remplacez `N` par le numéro de la vidéo retourné dans la réponse de l'upload ou de la liste.

**Exemple curl :**
```bash
curl http://localhost:5000/hls/video1/index.m3u8
```

Pour lire le flux dans VLC ou un lecteur compatible HLS, utilisez l'URL complète :
```
http://localhost:5000/hls/video1/index.m3u8
```

### 4. Accès à l'image de preview

**GET** `/hls/videoN/preview.jpg`

- Remplacez `N` par le numéro de la vidéo.

**Exemple curl :**
```bash
curl http://localhost:5000/hls/video1/preview.jpg --output preview.jpg
```

---

## Structure des dossiers
- `uploads/` : vidéos MP4 uploadées
- `hls/` : dossiers contenant les fichiers HLS générés (playlist `.m3u8`, segments `.ts`, et `preview.jpg`), nommés `video1`, `video2`, etc.

## Notes
- Les fichiers HLS sont générés à la volée lors de l'upload.
- Vous pouvez supprimer les dossiers dans `hls/` pour libérer de l'espace si besoin.
- Le nom du dossier HLS n'est plus basé sur le nom du fichier, mais sur un compteur automatique (video1, video2, ...).
- L'image de preview est générée automatiquement lors de l'upload (première seconde de la vidéo). 