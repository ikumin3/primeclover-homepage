+++
draft = false
thumbnail = "2023/08/Studying-Polymorphism-in-Cpp-Factory-Pattern/thumbnail.png"
tags = ["C/C++","オブジェクト指向"]
categories = "プログラム"
date = "2023-08-13T04:12:08+09:00"
title = "C++でポリモーフィズムの勉強（With Factoryパターン）"
description = "C++でポリモーフィズムの勉強（With Factoryパターン）"
toc = true
archives = ["2023/08"]
+++

四則演算をする計算機クラスを作成して、ポリモーフィズムを体感してみる。
色々改変重ねるうちに、クライアント側に具体的なクラス書きたくないよな...
ってなってデザインパターンの一つであるFactoryMethodを試してみた。

とりあえず具体的な計算機クラスを作成してみる。省略のために加算のみ作成。
簡単なものなので今回はヘッダー側にそのまま定義も書いている。

アプリ側はそのまま計算機クラスを作成。これから下記に示すコードは思い出しながら適当に書いたので、ビルド未確認。

## 愚直に計算機（加算のみ）を作成してみる

```cpp
# Calc.h
class Calc
{
public:
	Calc() {
	};
	~Calc() {};

	int add(int x, int y) {
		return x + y;
	}

};

# app.cpp
int main(){
	Calc* calc = new Calc();

	cout << calc.add(1,3) << endl;

	delete calc;
}
```

## 基底・派生クラスで書いてみる
次に、アプリ側で具体的なクラス（Calc）に依存しているので、変更に強くするためにインタフェースを用意してアプリ側のコードを極力触らなくても変更できるよう改変してみる。
とりあえずインタフェースクラス（ICalc）を用意してCalcに継承させてみる。ICalcは純粋仮想関数なので、Calc側で必ず定義する必要が出てくる。これによって実装できてない、みたいなミスも減らせる。

クライアント側のコードを見てみると、new Calc(); だけに収まっている。これでちょっと変更に強くなった？
今はただのCalcしかいないのであんまり恩恵が見られないけど、ICalcを継承した計算機を複数用意して、リストで管理、みたいなことも出来たりすると思う。
後は基底クラスで派生先のオブジェクトをいじったりだとか。

```cpp
# Calc.h

class Calc : public ICalc 
{
public:
	Calc() {
	};
	~Calc() {};

	int add(int x, int y) {
		return x + y;
	}

# ICalc.h
class ICalc{
	virtual int add(int x, int y) = 0;
};

# app.cpp
int main(){
	ICalc* calc = new Calc();

	cout << calc.add(1,3) << endl;	

	delete calc;
}
```

ただ、まだCalcクラスはまだapp側に残ってしまっている。生成に関するコードはまだ隠せていない。
そこで、Factoryパターンを用いて隠微を試みてみる。Factoryパターンは生成に関するコードを隠微することができるデザインパターンの一つらしい。

## Factoryパターンを書いてみる

```cpp
# Calc.h
/* Calcクラス */
class Calc : public ICalc 
{
public:
	Calc() {
	};
	~Calc() {};

	int add(int x, int y) {
		return x + y;
	}
};

# ICalc.h
/* Calcの抽象クラス */
class ICalc{
public:
	virtual int add(int x, int y) = 0;
};

# CalcFactory.h
/* Calcを生成する */
class CalcFactory : public ICalcFactory{
public:
	ICalc* createCalc() { return new Calc();}
};

# ICalcFactory.h
/* CalcFactoryの抽象クラス */
class ICalcFactory {
public:
	virtual ICalc* createCalc() = 0;
};

# app.cpp
int main(){
	ICalcFactory* factory = new CalcFactory();
	ICalc* calc = factory->createCalc();

	cout << calc->add(1,3) << endl;	

	delete calc;
	delete factory;
}
```

Facrtoryパターンによって、クライアント側のコードの変更はほとんど無くなる。ICalcな計算機を入れ替えたいみたいなことが置きたらcreateCalcの中身を変えてあげれば良い。

使い道は～...。
いずれ変更するかもっていうオブジェクトをFactoryパターンで書いてあげることぐらい？


## その他
ポリモーフィズムではないけれど、より再利用性を高めるならばaddやsubといった関数はtemplateにしてあげることで、わざわざ別のプリミティブな型を用意せずとも対応することも可能だと思う。

雑ですが、ひとまずポリモーフィズムとFactoryパターンについて触れたのでちょっとまとめてみました。