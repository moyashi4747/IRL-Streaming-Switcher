# IRL-Streaming-Switcher　ってなに
外出先から IRL 配信をするときはどうしても通信が不安定なため配信の途絶が起きてしまう。
配信が止まると視聴者は配信を見辛く、さらに長時間途絶すると配信枠自体が終了してしまう。
これを防ぐため、RTMP 中継サーバーを構築し配信の途絶を検知した場合、待機中画面を配信先に配信することで
配信の途切れと配信枠の意図しない終了を防ぐ python スクリプトです。

# 環境例
AWSインスタンス: Ubuntu 24.04
サイズ: t3.xlarge

t3.medeium でもいけるけどスペックぎりぎりかも

# セットアップ
## Nginx-rtmp と FFmpeg を導入

`sudo apt install -y nginx libnginx-mod-rtmp ffmpeg`

## Nginx 設定ファイルを編集
`/etc/nginx/nginx.conf`に以下を設定を追加。

```
rtmp {
    server {
        listen 1935;
        chunk_size 4096;
        application live {
            live on;
            record off;
            hls on;
            hls_path /tmp/hls;
            hls_fragment 2;
            hls_playlist_length 6;
            hls_cleanup on;
            hls_continuous on;
        }
    }
}
http {
    server {
        listen 8080;

        location /stat {
            rtmp_stat all;
            rtmp_stat_stylesheet stat.xsl;
        }

        location /stat.xsl {
            root /usr/local/src/nginx-rtmp-module/;
        }
        location /hls {
            types {
                application/vnd.apple.mpegurl m3u8;
                video/mp2t ts;
            }
            root /tmp;
            add_header Cache-Control no-cache;
        }
    }
}
```

## Nginx のステータス確認用の stat.xsl を配置
```
sudo mkdir -p /usr/local/src/nginx-rtmp-module
sudo wget https://raw.githubusercontent.com/arut/nginx-rtmp-module/master/stat.xsl \
  -O /usr/local/src/nginx-rtmp-module/stat.xsl
```
実行したら Nginx を再起動
```
sudo nginx -t
sudo systemctl restart nginx
```

## お好みの待機画面を配置
スクリプトでは`/home/ubuntu`に`Offline.png`を配置

## リポジトリの python スクリプトを設定部分を修正して配置
```
# Configuration
STREAM_NAME = "STREAM KEY NAME"  # 外出先から中継RTMPサーバーに送信するストリームキーを記入
HLS_URL = "http://localhost:8080/hls/{STREAM_NAME}.m3u8"
STREAM_URL = "rtmp://{Stream URL}" #配信するサイトの RTMP URL
OFFLINE_IMAGE = "/home/ubuntu/offline.png"  # 待機画面のパス
```

# つかいかた
1. スマートフォン、カメラなどから `rtmp://{AWSサーバーのIPアドレス}/live/{スクリプトで設定したストリームキー}`に配信。
2. SSH などでターミナルにアクセスし、`nohup python3 ~/irl_stream_switcher.py &`でpythonスクリプトを実行。
3. 配信終了時は`pkill -f irl_stream_switcher.py`、`pkill -f ffmpeg`により実行を止める。




 


