## ysynth4

RaspberryPiとTimidity++を核にしたハードウェアシンセサイザーです。GM/GS/XG/エクスクルーシブのメッセージが使えます。

## ライセンス
ysynth4は複数のソフトウェアで構成されています。他のソフトウェアのライセンスはそのソフトウェアの元々のライセンスに準じます。ysynth4のソースコードそのものは[MITライセンス](https://github.com/YoutechA320U/ysynth4/blob/master/LICENSE)となっています。

## 概要
RaspberryPi 3Bで動作するハードウェアシンセサイザーです。チャンネルごとにデータを送信、ディスプレイに表示するMIDIコントローラとしての機能と、チャンネルごとにデータを受信、ディスプレイに表示し、任意のサウンドフォント(.sf2)を鳴らせるMIDI音源としての機能、任意のMIDIファイルを自身や外部音源で演奏できるMIDIシーケンサーとしての機能を持ちます。


![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/ysynth4_hard.jpg "作例")

## スペック
    *GM/GS/XG/エクスクルーシブメッセージ対応*
    *Timidity++ version 2.14.0*
    
    システム:RaspberryPi 3B+, Raspbian buster Lite
    パート数:16
    最大同時発音数:128
    音源:サウンドフォント(.sf2) ※任意の数のファイルを追加可能
    サンプリングレート:32000Hz
    本体で操作、表示できるMIDIメッセージ:プログラムチェンジ、ボリューム、エクスプレッション、パン、モジュレーション、リバーブ、
                                      コーラス、ディレイ、ピッチベンド
    ディスプレイ:1.8インチ160x128フルカラーグラフィックディスプレイ
    接続端子:MIDI-IN/OUT、microUSBTypeB-MIDI端子、USB2.0TypeAx4(1つはUSBメモリ用)、イーサネット、3.5mmステレオオーディオ出力端子（本体orPi-DAC+）、RCA(Pi-DAC+)
    電源:DC5V2.4A
    シーケンサー:MIDIファイルを再生可能 ※任意の数のファイルを追加可能

## 開発環境
    OS : Raspbian buster Lite
    RaspberryPi : RaspberryPi 3B+
    Python : ver3.7
    
## 回路図
![SS](https://github.com/YoutechA320U/ysynth4/blob/master/SS/circuit.png "回路図")

## 必要な部品

## インストール方法
※OSはRaspbian buster Lite前提です。

1. RaspberryPiをネットワークに接続して以下のコマンドを実行します。

    sudo apt-get update

    sudo apt-get upgrade -y

    sudo apt-get install -y git
    
    git clone --recursive --depth 1 https://github.com/YoutechA320U/ysynth4.git

2. `sudo sh /home/pi/ysynth4/setup.sh`でセットアップスクリプトを実行します。完了すると自動的に再起動します。

3. ディスプレイにメッセージが表示されたら完了です。

## 操作方法

## 使い方

## 備考

### 参考コード・資料

## 履歴
    [2019/08/23] - 初回リリース(Ver.1.1)
    [2018/08/24] - 調整(Ver.1.2)