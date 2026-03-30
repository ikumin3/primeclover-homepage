+++
draft = false
thumbnail = "2023/08/What-is-Ring-Buffer-Explained/thumbnail.png"
tags = ["C/C++","プログラム"]
categories = "プログラム"
date = "2023-08-16T05:10:12+09:00"
title = "リングバッファって何なのさ？"
description = "リングバッファって何なのさ？"
toc = true
archives = ["2023/08"]
+++

# リングバッファ

昔仕事で使ったんだけど、調べ物してるときに出てきたので復習がてらまとめてみる。ついでにC++の練習も兼ねてやってみる。

## 概要

リングバッファのわかりやすい説明はこちら。

[循環バッファ](https://ufcpp.net/study/algorithm/col_circular.html)
C#だけど、構造とか概要とかざっくり理解できるのでおすすめ。

リングバッファとは、データ構造の一つで、循環バッファっていう名前で呼ばれていたりもする。

配列とは異なり、先頭と末尾を繋げたような構造、つまりリング状のような構造のことを指している。配列なので基本的には先頭から順にデータを格納するけど、リングバッファは末尾まで行ったら再び先頭に戻って格納していく。そのため再び先頭に入れた場合はデータが上書きされていく。

あくまでイメージだけど、概念図としては下記（[Wikipedia](https://ja.wikipedia.org/wiki/%E3%83%AA%E3%83%B3%E3%82%B0%E3%83%90%E3%83%83%E3%83%95%E3%82%A1)より引用）のような感じ。
配列は直線で終わっちゃうけど、先頭と末尾をつなげるとリング状になる。

![[https://ja.wikipedia.org/wiki/リングバッファ](https://ja.wikipedia.org/wiki/%E3%83%AA%E3%83%B3%E3%82%B0%E3%83%90%E3%83%83%E3%83%95%E3%82%A1)](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Circular_buffer.svg/220px-Circular_buffer.svg.png)![[https://ja.wikipedia.org/wiki/リングバッファ](https://ja.wikipedia.org/wiki/%E3%83%AA%E3%83%B3%E3%82%B0%E3%83%90%E3%83%83%E3%83%95%E3%82%A1)](https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Circular_buffer_-_empty.svg/220px-Circular_buffer_-_empty.svg.png)

## 利点

- サイズが予め固定なので、メモリ使用量の予測がしやすい
- 使用量抑えつつも配列やリストを用いたものよりは高速、らしい。
確かに作成してみてわかったけど、インデクスの算出ぐらいしかやってないから、連結リストとか動的配列のような管理よりは高速なのかも。

## 用途

- リアルタイムシステムで一時的な格納で使う
オーディオ処理とかネットワーク通信処理とか

## その他参考文献

[C++でスレッドセーフなリングバッファを実装してみた - a-advent-2019](https://scrapbox.io/a-advent-2019/C++でスレッドセーフなリングバッファを実装してみた)

## memo

### ラフ

なんとなくこんな感じなのかなーっていうラフを書いてみる。

```cpp
int main()
{
	int buffer[SIZE] = { 0 };
	int head = 0;
	int tail = 0;
	int data = 0;

	/* Write */
	buffer[head] = data;
	head = (head + 1) % SIZE; // head = SIZEは0に戻る

	/* Read */
	data = buffer[tail];
	tail = (tail + 1) % SIZE; // tail = SIZEは0に戻る
}
```

### ラフ2　クラスにしてみる

リングバッファクラスを作成してみて、長さ3のリングバッファを作成。
そのリングバッファに対して5回書き込んで、5回読み込んで出力してみる。
確かに末尾にたどり着いたら正しく先頭に書き込んでいることがわかった。
（というかnewしてるんだから、deleteしないと駄目ですね...。）

```cpp
main.cpp

#include "ring_buffer.h"
#include <iostream>
#define SIZE (3)

int main()
{
	RingBuffer* rb = new RingBuffer(SIZE);

	/* Write Buffer */
	for(int i = 0; i < 5; i++) {
		std::cout << "Writing : " << i << std::endl;
		rb->writeBuffer(i);
	}
	// 0,1,2
	// 3,1,2
	// 3,4,2

	/* Read Buffer */
	for(int i = 0; i < 5; i++) {
		std::cout << "Reading : " << rb->readBuffer() << std::endl;
	}
	// 3,4,2,3,4
}
```

```cpp
ring_buffer.h

#pragma once

#include <vector>

class RingBuffer
{
private:
	std::vector<int> _buffer;
	int _head = 0;
	int _tail = 0;
	int _size = 0;

public:
	RingBuffer(int size)
	{
		_size = size;
		_buffer.resize(_size);
	}

	~RingBuffer() {};

public:
	void writeBuffer(int data)
	{
		_buffer[_head] = data;
		_head = (_head + 1) % _size;
	};

	int readBuffer()
	{
		int data = _buffer[_tail];
		_tail = (_tail + 1) % _size;
		return data;
	};
};
```

- メンバ変数とローカル変数の意識

書いてる途中で、メンバにするかどうか迷ったのでメモ
この使い方であれば、_dataは返してるだけで他のメソッドとかでは使うことはないので、RingBufferクラスがインスタンスごとにdataを保持する必要はないなあということに気づいた。

```cpp

/* 良くない書き方 */
int readBuffer()
	{
		_data = _buffer[_tail];
		_tail = (_tail + 1) % _size;
		return _data;
	};

/* こちらの方が良い */
int readBuffer()
	{
		int data = _buffer[_tail];
		_tail = (_tail + 1) % _size;
		return data;
	};
```