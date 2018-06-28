Thanks [libpytunes](https://github.com/liamks/libpytunes) for idea.

This script allows you to copy selected playlists from Itunes to any folder.
I use it for sync my playlist with my android. On android you should share any folder somehow (smb protocol e.g.).
I use [Pocketshare](https://play.google.com/store/apps/details?id=info.appcube.pocketshare) for remote sync.

You can add environment variables:
* `ITUNES_LIB_PATH` - if your itunes library locates not in default folder.
* `SYNC_FOLDER` - folder on target where playlist will be saved. If not set you can point manually.

Script will copy all songs from selected playlists if they not exists and will create or rewrite playlist file in `m3u8` format.
