"""
配置模型文件
客户可修改的配置文件

软件所允许的目录下方，有一个隐藏的 .json 文件
该文件键不加密，但是值是加密的，所以无需担心被修改

隐藏文件(.json)     <==进行加/解密==>    内存对象(Config)
"""
import json
import typing as t
from pathlib import Path
from .models import Cell, Preset
from .utils import resource_path

# 任务栏上、窗口上的图标（重新打包后才能生效）
# ./ 表示运行时的工作目录 ./assets/ 表示工作目录(项目入口所在目录)中的 assets 文件夹
ICON_PATH = resource_path('./assets/images/icon.ico')

# 网站名称
SITE = "游戏仓鼠"
# 广告链接
URL = "www.examples.com"
# 应用显示名称
APP_NAME = f'MD5 file integrity checker (文件完整性校验) - 【{SITE}: {URL}】'

# 顶部图片路径(仅代码中配置)
LOGO = resource_path('./assets/images/logo.png')

# 左侧底部红色文字提示词
BOTTOM_HINT = '文件校验完毕后出现"校验失败"请勿解压，务必等待校验通过方可解压'
# 点击左侧底部红字后是否可以跳转到指定网址，如果为空，则不会跳转
BOTTOM_HINT_LINK = ''
# 配置上述链接后，这段代码将启用，样式在下方设置，color 表示文字颜色
HTML_BOTTOM_HINT = f"""
<span style="margin-left: 10px; color: red; font-size: 10pt;">
    <a href="{BOTTOM_HINT_LINK}" style="color: red; text-decoration: none;">
        {BOTTOM_HINT}
    </a>
</span>
"""
REAL_BOTTOM_HINT = BOTTOM_HINT if not BOTTOM_HINT_LINK else HTML_BOTTOM_HINT

# 校验过程 5 个状态对应的显示名和文字颜色
STATE_STYLES = {
    -2: Cell('程序异常', 'red'),
    -1: Cell('校验失败', 'red'),
    0: Cell('未校验', 'black'),
    1: Cell('校验成功', '#008000'),
    2: Cell('校验中', 'orange'),
}
DEFAULT_CELL = Cell('未知状态', 'blue')


class Config:
    _path = Path(resource_path('./assets/presets.json'))
    presets: t.List[Preset] = []  # 预设列表，读取 json 文件会加载

    @classmethod
    def read_json(cls):
        if not cls._path.exists():
            return None

        with cls._path.open('r', encoding='utf-8') as fr:
            data = json.load(fr)

        raw_presets = data.get('presets')
        if raw_presets:
            cls.presets = [Preset(preset['filename'], preset['data_md5']) for preset in raw_presets]
