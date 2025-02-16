# AIチャット

PydanticAI、NiceGUI、Ollama、jageocoderを使った、AIチャットです。

## 準備

### uvのインストール

下記からインストールしてください。

https://docs.astral.sh/uv/getting-started/installation/

### Ollamaのインストール

下記からダウンロードしてインストールしてください。

https://ollama.com/

### jageocoderのサーバーの準備

下記のようにjageocoderのサーバーをローカルに準備してください。

**手順**

* https://github.com/t-sagara/jageocoder-server/archive/refs/heads/main.zip をダウンロードし解凍
* https://www.info-proto.com/static/jageocoder/20230702/v2/gaiku_all_v20.zip をダウンロードしZIPのまま上記のdataに移動
* https://www.info-proto.com/static/jageocoder/20230702/v2/jukyo_all_v20.zip をダウンロードしZIPのまま上記のdataに移動

**参考**

https://t-sagara.github.io/jageocoder/

## サービス開始

Ollamaのサービスを開始するには、下記を実行してください。

```
ollama serve
```

jageocoderのサービスを開始するには、`docker-compose.yml`の存在するところで下記を実行してください。

```
docker compose up -d
```

## チャット実行

チャットを実行するには下記を実行してください。

```
uv run chat
```

`東京都からさいたま市までの距離は?`のように質問して、`19.56km`と答えれば正解です。
