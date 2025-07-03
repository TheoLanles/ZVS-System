# API de Streaming Vidéo HLS avec Flask

Ce projet propose une API simple pour convertir des vidéos en HLS (HTTP Live Streaming) et les diffuser via Flask.

## Prérequis

- Python 3.x
- [ffmpeg](https://ffmpeg.org/) installé et accessible dans le PATH
- Dépendances Python :
  ```bash
  pip install flask
  ```

## Formats vidéo compatibles

L'API accepte les formats vidéo suivants (dépend de la prise en charge par ffmpeg) :
- MP4
- MOV
- AVI
- MKV
- FLV
- WebM

> **Remarque** : Si vous rencontrez une erreur lors de l'upload, vérifiez que le format est bien supporté par ffmpeg.

## Lancer le serveur

```bash
python app.py
```

## Configuration de la base URL

Par défaut, la base URL est `http://localhost:5000`.
Pour un accès distant ou via un reverse proxy, adaptez la base URL dans vos requêtes et dans la configuration du client (frontend, lecteur vidéo, etc.).

Exemple :
- En local : `http://localhost:5000/hls/video1/index.m3u8`
- Sur un serveur : `https://votre-domaine.com/hls/video1/index.m3u8`

## Endpoints

### 1. Upload d'une vidéo et conversion en HLS

**POST** `/upload`

- Form-data :
  - `file` : fichier vidéo à uploader (formats compatibles listés ci-dessus)

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
- `subtitle_url` : URL du fichier de sous-titres (ou null si absent)

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
    "preview_url": "http://localhost:5000/hls/video1/preview.jpg",
    "subtitle_url": "http://localhost:5000/hls/video1/subtitles.vtt"
  },
  {
    "id": "video2",
    "title": "Video 2",
    "hls_url": "http://localhost:5000/hls/video2/index.m3u8",
    "preview_url": "http://localhost:5000/hls/video2/preview.jpg",
    "subtitle_url": "http://localhost:5000/hls/video2/subtitles.vtt"
  }
]
```

### 3. Accès au flux HLS

**GET** `/hls/videoN/index.m3u8`

- Remplacez `N` par le numéro de la vidéo.

### 4. Accès à l'image de preview

**GET** `/hls/videoN/preview.jpg`

- Remplacez `N` par le numéro de la vidéo.

### 5. Accès ou mise à jour des sous-titres (si supporté)

**GET** `/hls/videoN/subtitles.vtt`

- Remplacez `N` par le numéro de la vidéo.
- Si le fichier de sous-titres existe, il sera servi au format WebVTT.

**POST** `/hls/videoN/subtitles.vtt`

- Permet d'ajouter ou de mettre à jour les sous-titres pour une vidéo donnée.
- Form-data :
  - `file` : fichier de sous-titres au format `.vtt`

**Exemple curl :**
```bash
curl -X POST -F "file=@/chemin/vers/sous-titres.vtt" http://localhost:5000/hls/video1/subtitles.vtt
```

---

## Structure des dossiers
- `uploads/` : vidéos uploadées
- `hls/` : dossiers contenant les fichiers HLS générés (playlist `.m3u8`, segments `.ts`, `preview.jpg`, et éventuellement `subtitles.vtt`), nommés `video1`, `video2`, etc.

## Notes
- Les fichiers HLS sont générés à la volée lors de l'upload.
- Vous pouvez supprimer les dossiers dans `hls/` pour libérer de l'espace si besoin.
- Le nom du dossier HLS n'est plus basé sur le nom du fichier, mais sur un compteur automatique (video1, video2, ...).
- L'image de preview est générée automatiquement lors de l'upload (première seconde de la vidéo).
- Les sous-titres peuvent être ajoutés ou mis à jour via l'endpoint dédié (voir ci-dessus). 
