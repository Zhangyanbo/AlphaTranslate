# AlphaTranslate

基于多次迭代、内部反馈的LLM翻译Agent。

## 使用方法

1. 将需要翻译的文本保存到`data/article.md`中。
2. 运行`translate.py`，等待翻译完成。
3. 翻译结果将保存到`data/final_result.md`中。
4. 翻译过程将保存到`data/final_process.json`中。

## 核心框架

本方法的核心在于迭代。反复润色、反馈、选择，最终得到满意的结果。其核心代码是：

```python
agent = Sequential(
        TranslateLayer(client, reference),
        CollabLayer(client, n=8, reference=reference),
        CollabLayer(client, n=8, reference=reference),
        CollabLayer(client, n=8, reference=reference),
    )
```
其中的`TranslateLayer`负责直接翻译，而后面每一个`CollabLayer`负责一次迭代。
在每一次迭代中，我们使用`ProfessorLayer`生成多个更符合汉语习惯的翻译结果，然后使用`ChooserLayer`选择最优的翻译结果。