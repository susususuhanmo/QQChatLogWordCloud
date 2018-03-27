#coding:utf-8
__author__ = 'Su'
import jieba    #分词包
import numpy    #numpy计算包
import codecs   #codecs提供的open方法来指定打开的文件的语言编码，它会在读取的时候自动转换为内部unicode
import pandas   
import matplotlib.pyplot as plt
import PIL.Image as Image
from wordcloud import WordCloud#词云包
import re


#从指定目录下读取导出的txt格式聊天文件
#注意使用 'utf-8'编码读取，或者 'rb'方法二进制读取，否则默认gbk读取会无法解析
file=codecs.open(u"C://Users//Administrator//Desktop//最终幻想小分队.txt",'r','utf-8')
content=file.read()
file.close()



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




# 通过pandas将list转化为DataFrame
words_df=pandas.DataFrame({'segment':segment})


# 读入停词文件，过滤掉一些无用关键词。
stopwords=pandas.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\t",names=['stopword'],encoding="utf8")
words_df=words_df[~words_df.segment.isin(stopwords.stopword)]

# 对词语进行数量统计并按照数量排序
words_stat=words_df.groupby(by=['segment'])['segment'].agg(['size'])
words_stat=words_stat.reset_index().sort_values(by="size",ascending=False)

# 设置形状和配色图片
coloring=numpy.array(Image.open("moguli.jpg"))

# 设置词云属性
wordcloud=WordCloud(
mask = coloring, #设置词云形状
font_path="simhei.ttf",max_font_size=120, margin=1,scale=32,background_color='white', mode="RGBA" )

# 将padas的DataFrame转化为词云所需要的字典格式
word_frequence = {x[0]: x[1] for x in words_stat.head(4000).values}

# 读入数据生成词云
wordcloud=wordcloud.fit_words(word_frequence)

# 两种生成方式
# 1、生成默认配色的词云
#plt.imshow(wordcloud)

# 2、生成以图片颜色配色的词云
from wordcloud import WordCloud,ImageColorGenerator
plt.axis("off")
plt.imshow(wordcloud.recolor(color_func=ImageColorGenerator(coloring)))


#两种输出图片方式
# 1、指定精度进行输出
# plt.savefig("E:/temp.jpg",dpi=600)

# 2、完整图片输出
wordcloud.to_file("E:/temp.png")

#预览图片
plt.show()