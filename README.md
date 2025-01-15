# AutoDo 文档

本文档提供了详细的函数说明、参数说明和使用指南。

## 函数文档

### process_templates
处理模板文件并替换指定参数。

参数说明：
- `template_dir` (str): 模板文件所在目录
- `output_dir` (str): 处理后文件的保存目录
- `params` (dict): 用于替换模板中的参数字典
  - 示例: `{"project_name": "MyProject", "author": "张三"}`

### find_files
在指定目录中搜索文件。

参数说明：
- `directory` (str): 搜索的根目录
- `pattern` (str): 文件匹配模式 (例如: "*.py", "*.txt")
- `recursive` (bool, 可选): 是否搜索子目录 (默认: True)

返回值：
- 匹配文件路径列表

### read_config
读取配置文件。

参数说明：
- `config_path` (str): 配置文件路径
- `format` (str, 可选): 配置文件格式 ('json', 'yaml', 默认: 'json')

返回值：
- 包含配置数据的字典

### write_output
将数据写入输出文件。

参数说明：
- `data` (Any): 要写入的数据
- `output_path` (str): 输出文件路径
- `mode` (str, 可选): 文件打开模式 (默认: 'w')

### validate_params
验证输入参数是否符合模式。

参数说明：
- `params` (dict): 待验证的参数
- `schema` (dict): 验证模式
- `strict` (bool, 可选): 是否使用严格验证 (默认: True)

返回值：
- bool: 验证通过返回True，否则返回False

## 使用指南

### 基本用法

1. 首先，准备模板文件目录：
```bash
templates/
  ├── config.template
  └── script.template
```

2. 创建配置文件 (config.json):
```json
{
  "project_name": "我的项目",
  "author": "张三",
  "version": "1.0.0"
}
```

3. 处理模板：
```python
from auto_do import process_templates

# 读取配置
config = read_config("config.json")

# 处理模板
process_templates(
    template_dir="templates",
    output_dir="output",
    params=config
)
```

### 高级用法

#### 自定义模板处理
```python
# 带参数验证的处理
params = {
    "project_name": "自定义项目",
    "author": "张三",
    "custom_fields": {
        "description": "这是一个自定义项目"
    }
}

# 处理前验证参数
if validate_params(params, schema):
    process_templates("templates", "output", params)
```

#### 文件操作
```python
# 查找特定文件
python_files = find_files("src", "*.py", recursive=True)

# 处理多种文件类型
for file_pattern in ["*.py", "*.js", "*.css"]:
    files = find_files("src", file_pattern)
    # 针对不同文件类型进行处理
```

## 最佳实践

1. **模板组织**
   - 将模板文件放在专门的目录中
   - 使用清晰、描述性的模板名称
   - 相关模板分组放在子目录中

2. **参数管理**
   - 处理前始终验证参数
   - 复杂参数集使用配置文件
   - 敏感信息存放在单独的配置文件中

3. **错误处理**
   - 始终检查函数返回值
   - 实现适当的文件操作错误处理
   - 处理前验证输入参数

4. **输出管理**
   - 使用清晰的输出目录结构
   - 为重要文件实现备份机制
   - 处理后清理临时文件

## 常见问题及解决方案

1. **找不到模板**
   - 验证模板目录路径
   - 检查文件权限
   - 确保模板文件存在

2. **参数验证失败**
   - 检查参数类型是否匹配模式
   - 验证是否提供了必需参数
   - 检查参数命名约定

3. **输出目录问题**
   - 确保输出目录存在
   - 检查写入权限
   - 验证磁盘空间是否充足

## 贡献指南

请按以下步骤贡献代码：
1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件
