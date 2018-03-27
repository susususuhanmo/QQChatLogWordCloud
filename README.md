# 使用python wordcloud模块将qq聊天记录生成关键词云
这个项目的github地址。https://github.com/susususuhanmo/QQChatLogWordCloud
#### 一、第一步导出qq聊天记录为txt(这部分没有技术含量，方法放在最后面了)
#### 二、准备需要的包
* pandas 、numpy: 这两个是用做数据分析非常常用也是必要的包。
* matplotlib：绘图包
* WordCloud: 本文最核心的生成词云的模块
* jieba：分词工具
#### 三、撸代码
##### 1、清洗聊天记录
读取文件
```python
#从指定目录下读取导出的txt格式聊天文件
#注意使用 'utf-8'编码读取，或者 'rb'方法二进制读取，否则默认gbk读取会无法解析
file=codecs.open(u"C://Users//Administrator//Desktop//最终幻想小分队.txt",'r','utf-8')
content=file.read()
file.close()
```
编写清洗函数，清洗聊天数据。主要是需要清洗掉一些无用的关键词：
* 2017-11-06 12:54:48 蠢货(123456789) 类似这个格式的昵称信息
* 图片，表情，红包，投票信息
* @别人的信息，这个看情况把，我不太喜欢昵称出现在最后的词云里
```python
#定义聊天文件处理函数：
# 1、使用正则去除聊天文件中的昵称信息
# 2、然后使用正则去掉@信息
# 3、替换掉txt中无法显示的图片和表情
def replaceQQStr(str):
    withoutNameInfo =re.sub(r'^\d{4}-\d{2}-\d{2} \d{1,2}:\d{1,2}:\d{1,2} .*[\(\<][1-9][0-9]{4,}[\)\>]', "", str)
    return re.sub(r'@.* ',"",withoutNameInfo)\
        .replace("[图片]","").replace("[表情]","").strip()

#将读入的txt按行分开，对每行进行处理，并过滤掉投票和红包信息。
lines = content.split("\n")
cleanedLines =[]
for line in lines:
    replacedStr = replaceQQStr(line)
    if replacedStr!= "" and ('参加了投票' not in replacedStr) and ('[QQ红包]' not in replacedStr):
        cleanedLines.append(replacedStr)
```
##### 2、对干净的聊天记录进行分词统计
分词，分词结果如果出现一些特有的词语截了一半或者截多了几个字符的情况，可以手动添加分词词库。
```python
# 为切词加入未能准确识别的特有关键词
# 下面是最终幻想游戏中的一些关键词，我们将它们添加进去。
jieba.suggest_freq('拉拉肥', True)
jieba.suggest_freq('24人本', True)
jieba.suggest_freq('4人本', True)
jieba.suggest_freq('四人本', True)
jieba.suggest_freq('8人本', True)
jieba.suggest_freq('八人本', True)
jieba.suggest_freq('二十四人本', True)

# 对清洗过的聊天文件逐行进行切词，获得切好的词list
segment=[]
for cleanedLine in cleanedLines:
    words = jieba.cut(cleanedLine)
    for word in words:
        if len(word) > 1 and word != '\r\n':
            segment.append(word)
```
根据关键词数据，建立pandas的DataFrame，通过停词词库过滤掉一些中文中不适合做关键词的词语，进行关键词数统计并根据次数排序。
```python
# 通过pandas将list转化为DataFrame
words_df=pandas.DataFrame({'segment':segment})

# 读入停词文件，过滤掉一些无用关键词。
stopwords=pandas.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\t",names=['stopword'],encoding="utf8")
words_df=words_df[~words_df.segment.isin(stopwords.stopword)]

# 对词语进行数量统计并按照数量排序
words_stat=words_df.groupby(by=['segment'])['segment'].agg(['size'])
words_stat=words_stat.reset_index().sort_values(by="size",ascending=False)

# 将padas的DataFrame转化为词云所需要的字典格式
word_frequence = {x[0]: x[1] for x in words_stat.head(4000).values}
```
##### 3、使用WordCloud生成词云图片
```python
# 设置词云属性
wordcloud=WordCloud(
font_path="simhei.ttf",
margin=1,
scale=32,
background_color="white",
 mode="RGBA" )

# 词云对象读入数据
wordcloud=wordcloud.fit_words(word_frequence)

#生成词云
plt.imshow(wordcloud)

#两种输出图片方式
# 1、指定精度进行输出
# plt.savefig("E:/temp.jpg",dpi=600)
# 2、完整图片输出
wordcloud.to_file("E:/temp.png")
#预览图片
plt.show()
```
词云属性解释
* **font_path**:字体路径
* **max_font_size**:最大字号,这个我是有做调整的，有时默认生成出来会觉得，关键词大小都差不多，没有突出的关键词，没有那种词云的感觉。就像下图那样。
![temp.png](https://upload-images.jianshu.io/upload_images/11344477-76cc93c5a315211e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

调整成120之后就好看很多，有很明显的差别。
![temp.png](https://upload-images.jianshu.io/upload_images/11344477-fb0f5bbd18dcdb23.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
* **margin**:词间间距
* **scale**:精度级别？比例？我不知道具体该怎么翻译，反正越大越清楚。运行速度越慢
* **background_color**:背景颜色，如果想弄透明需要这里填None,然后后面的选项填RGBA,A代表透明度，只有RGBA的模式才能有透明背景。
```python
wordcloud=WordCloud(
font_path="simhei.ttf",
margin=1,
scale=32,
background_color=None,
 mode="RGBA" )
```
* **mode**:颜色模式默认"RGB"，想弄透明背景需要选择"RGBA"
* **输出模式**：plt.savefig输出是指定精度输出，wordcloud.to_file为完整图片输出，每个词都能完全看清。
##### 4、设定词云形状颜色的生成方法
设置图片为可爱的莫古力
![moguli.jpg](https://upload-images.jianshu.io/upload_images/11344477-70e852f6d52bb954.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
根据这个莫古力的颜色分布，生成的词云如下，我这个不是特别好看，大家可以选择轮廓明显一点的图片来生成。
![temp.png](https://upload-images.jianshu.io/upload_images/11344477-6987c59d2d5f71fe.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



相比默认的模式，
* **图片形状**：这种方法需要用到numpy的array来读取图片，读去过后在设置中设置mask属性就可以设定词云形状
* **图片配色**：词云的配色要用到wordCloud中的ImageColorGenerator根据之前的图片数组来生成配色。
```python
# 设置形状和配色的图片路径
coloring=numpy.array(Image.open("moguli.jpg"))

# 设置词云属性
wordcloud=WordCloud(
mask = coloring, #设置词云形状为图片的数组
font_path="simhei.ttf", margin=1,scale=32,background_color=None, mode="RGBA" )

# 读入数据生成词云
wordcloud=wordcloud.fit_words(word_frequence)

# 生成以图片颜色配色的词云
from wordcloud import WordCloud,ImageColorGenerator
plt.axis("off")
plt.imshow(wordcloud.recolor(color_func=ImageColorGenerator(coloring)))
# 完整图片输出
wordcloud.to_file("E:/temp.png")

#预览图片
plt.show()
```

关于更详细的词云配置可以看这篇文章，这个作者对wordcloud的配置讲解的十分详细。
https://blog.csdn.net/heyuexianzi/article/details/76851377

##### 附qq聊天记录导出方法：
在你想导出的人或群处右键，点导出消息记录，
![导出聊天记录.jpg](https://upload-images.jianshu.io/upload_images/11344477-665269d6fbfa52fa.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
然后选择txt格式
![选择txt格式.jpg](https://upload-images.jianshu.io/upload_images/11344477-358de534aa4991b1.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
