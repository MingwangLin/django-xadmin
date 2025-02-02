class ImportErrMsg:
    NULL_REGION = '省, 市为必填项.'
    NULL_CITY = '国家, 省, 市为必填项.'
    NULL_BATCHREGION = '考区为必填项.'
    ERR_LEAF_BATCHREGION = '考区必须为叶子节点考区.'
    ERR_REGION = '省市区数据与行政区划名称参照表不一致.'
    FORBIDDEN_REGION = '省、市、区不在负责管辖区域内'
    ERR_NAME = '姓名为必填项, 且长度必须大于1.'
    INVALID_SCHEDULE = '日程有误, 格式要求为: YYYY/MM/DD HH:MM - YYYY/MM/DD HH:MM 或 YYYY/MM/DD HH:MM - HH:MM, 数据要求为: 开始时间小于结束时间.'
    INVALID_DATE = '日期有误, 格式要求为: YYYY/MM/DD. 数据要求为: 开始日期小于结束日期.'
    INVALID_FORMAT_DATE = '日期有误, 格式要求为: YYYY/MM/DD.'
    ERR_SCHEDULE = '批次没有该日程.'
    NULL_VENUE_NAME = '考站名称不允许为空.'
    ERR_VENUE_NAME = '考站名称须与考站信息中考站名称对应.'
    ERR_VENUE_CODE = '考站code有误.'
    ERR_VENUE = '考站名称和考站代码需至少填写一项.'
    NULL_ROOM_NAME = '考场名称不允许为空.'
    ERR_ROOM_NAME = '考站+考场名称不允许重复.'
    ERR_ROOM_ADDRESS = '考站+考场地址不允许重复.'
    NULL_ROOM = '考站对应的考场记录不允许为空.'
    NULL_VENDOR_NAME = '签约单位不允许为空.'
    NULL_ADDRESS = '地址/工作地点不允许为空.'
    NULL_WAREHOUSE = '仓库编码不允许为空.'
    ERR_WAREHOUSE_CODE = '仓库编码不存在.'
    ERR_WAREHOUSE_NAME = '仓库名称不允许为空且必须在悦站存在.'
    ERR_INVENTORY = '物资编码不允许为空且必须在悦站存在.'
    ERR_PS = '用途内的发货申请号不允许为空且必须在发货申请单中存在.'
    RIGHT_FORMAT_BUT_ERR_PS = '用途内的发货申请号必须在发运明细中存在.'
    ERR_DUPLICATED_PS = '用途内的发货申请号不允许重复.'
    NULL_CONTACTOR_NAME = '联系人姓名为不允许为空'
    NULL_EMAIL = '邮箱为必填项.'
    NULL_ZIPCODE = '邮编不允许为空.'
    ERR_PROPERTY = '类型为必填项, 只能填写:内聘/外聘.'
    ERR_GENDER = '性别为选填项, 只能填写:男/女, 或留空.'
    ERR_IS_NEW = '新监考为必填项, 只能填写:是/否.'
    DUPLICATED_EMAIL = '本行邮箱在本次导入数据中重复.'
    EXISTED_EMAIL = '该邮箱在系统中已存在督考人员账号.'
    ERR_EMAIL = '邮箱有误. 邮箱必须有@和.符号, 不能有空格'
    UNMATCHED_EMAIL = '姓名和邮箱不允许为空且必须在悦站存在.'
    NULL_PROPERTY = '性质不允许为空.'
    NULL_PHONE = '手机号不允许为空.'
    ERR_SEATCOUNT = '机位数需要为数字.'
    ERR_INVIGILATORCOUNT = '监考组长、监考数需为大于等于零的整数.'
    ERR_NOTENOUGHSEATS = '待编/已编状态下, 新导入的科次须大于等于原编排科次.'
    ERR_MODE_CONFLICT = '超编和备用机模式不能同时存在.'
    ERR_TASK_TYPE = '任务类型有误.'
    ERR_TYPE = '类型有误.'
    ERR_REQUIREMENTCOUNT = '需求数需要为大于0的整数.'
    ERR_STOCK_COUNT = '库存需要为大于等于0的整数.'
    ERR_CHECK_COUNT = '盘点数量需要为大于等于0的整数.'
    ERR_QUANTITY = '数量需要为大于0的整数.'
    ERR_USER = '盘点人需为悦站实际存在的人员..'
    ERR_DURATION = '工作天数/封场时长/考中时长/工作时长需要为大于0的数值, 且小数位最多为1位.'
    ERR_CARGO = '重量/体积/总费用/物资单价需要为数值.'
    ERR_FEE = '费用需要为大于0的数值.'
    NULL_FEE = '费用需至少填1项.'
    ERR_REVIEW_AND_PC_COUNT = '复核份数/机房数量/场次数需要为大于0的整数.'
    ERR_VENUE_TYPE = '考站类型有误.'
    UNMATCHED_REGION_AND_VENUE_TYPE = '行政区域与考站行政区域不匹配.'
    NULL_EXTERNAL_CODE = '内部运单号为必填项.'
    ERR_RECYCLE = '是否回收字段不允许为空且只能填:是/否.'
