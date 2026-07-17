#!/usr/bin/env python3
"""生成技能标签题库 SQL 文件"""

import os

OUTPUT = os.path.join(os.path.dirname(__file__), 'seed_skill_bank.sql')

# ========== 57 个标签 ==========
TAGS = [
    # 编程语言
    (1, 'Java',        '编程语言', 'Java 核心语法、面向对象、集合框架、泛型、注解、反射'),
    (2, 'C',           '编程语言', 'C 语言基础：指针、内存管理、结构体、预处理'),
    (3, 'C++',         '编程语言', 'C++ OOP、STL、智能指针、RAII、C++11/14/17 新特性'),
    (4, 'Python',      '编程语言', 'Python 装饰器、生成器、GIL、常用库(numpy/pandas/Django)'),
    (5, 'JavaScript',  '编程语言', 'JS 闭包、原型链、异步编程、ES6+、事件循环'),
    (6, 'TypeScript',  '编程语言', 'TypeScript 类型系统、泛型、工具类型、装饰器'),
    (7, 'Go',          '编程语言', 'Go 并发模型(goroutine/channel)、GMP 调度'),
    (8, 'Rust',        '编程语言', 'Rust 所有权、生命周期、借用检查、trait'),
    (9, 'Kotlin',      '编程语言', 'Kotlin 协程、空安全、扩展函数、与 Java 互操作'),
    (10,'PHP',         '编程语言', 'PHP 核心语法、Composer、Laravel/ThinkPHP、FPM'),

    # Java 生态
    (11,'JVM',         'Java生态', 'JVM 内存模型、类加载、GC、JIT 编译、性能调优'),
    (12,'Spring',      'Java生态', 'Spring IoC/AOP、事务管理、Bean 生命周期、设计模式'),
    (13,'Spring Boot', 'Java生态', 'Spring Boot 自动配置、Starter、Actuator、外部化配置'),
    (14,'Spring Cloud','Java生态', '微服务治理：服务注册发现、配置中心、网关、熔断降级'),
    (15,'MyBatis',     'Java生态', 'MyBatis 映射、动态 SQL、缓存、插件机制'),
    (16,'Hibernate',   'Java生态', 'Hibernate ORM、JPA、缓存、N+1 问题、延迟加载'),
    (17,'Maven',       'Java生态', 'Maven 依赖管理、生命周期、多模块构建'),
    (18,'Gradle',      'Java生态', 'Gradle 构建脚本、Task、插件、增量构建'),
    (19,'Java并发',    'Java生态', '线程池、锁机制、AQS、volatile、原子类、并发集合'),

    # 数据库
    (20,'MySQL',       '数据库', 'MySQL 索引、事务、锁、MVCC、SQL 优化、主从复制'),
    (21,'PostgreSQL',  '数据库', 'PostgreSQL 窗口函数、CTE、JSONB、扩展机制'),
    (22,'Redis',       '数据库', 'Redis 数据结构、持久化、集群、缓存策略、分布式锁'),
    (23,'MongoDB',     '数据库', 'MongoDB 文档模型、聚合管道、副本集、分片'),
    (24,'Elasticsearch','数据库','ES 倒排索引、查询 DSL、聚合分析、集群调优'),
    (25,'Oracle',      '数据库', 'Oracle 体系架构、PL/SQL、分区表、物化视图'),
    (26,'SQL',         '数据库', 'SQL 查询优化、复杂联表、子查询、窗口函数、索引设计'),

    # 中间件/基础设施
    (27,'Kafka',       '中间件', 'Kafka 生产消费、分区、副本、ISR、幂等、流处理'),
    (28,'RabbitMQ',    '中间件', 'RabbitMQ 交换机、死信队列、延迟队列、消息可靠性'),
    (29,'RocketMQ',    '中间件', 'RocketMQ 事务消息、顺序消息、延迟消息'),
    (30,'Nginx',       '中间件', 'Nginx 反向代理、负载均衡、HTTPS、性能调优'),
    (31,'Docker',      '中间件', 'Docker 镜像、Dockerfile、Compose、多阶段构建'),
    (32,'Kubernetes',  '中间件', 'K8s Pod/Deployment/Service、Helm、Ingress'),
    (33,'Zookeeper',   '中间件', 'ZooKeeper ZAB 协议、Watch、选举、分布式锁'),
    (34,'Linux',       '中间件', 'Linux 常用命令、Shell、文件系统、进程管理、性能分析'),

    # 前端
    (35,'HTML',        '前端', 'HTML5 语义化、表单、Canvas、Web Storage'),
    (36,'CSS',         '前端', 'CSS3 盒模型、Flex/Grid、动画、响应式、BFC'),
    (37,'Vue',         '前端', 'Vue 3 响应式、组合式 API、虚拟 DOM、Pinia'),
    (38,'React',       '前端', 'React Hooks、Fiber、虚拟 DOM、Redux/Zustand'),
    (39,'Angular',     '前端', 'Angular 模块化、DI、RxJS、路由守卫'),
    (40,'Webpack',     '前端', 'Webpack 打包、Loader/Plugin、代码分割、Tree Shaking'),
    (41,'Vite',        '前端', 'Vite ESBuild、HMR、Rollup、SSR'),
    (42,'Element Plus','前端', 'Element Plus 组件库、主题定制、表单校验'),
    (43,'ECharts',     '前端', 'ECharts 图表配置、数据绑定、自适应'),

    # 计算机基础
    (44,'数据结构',    '计算机基础', '数组/链表/树/图/哈希、时间复杂度、B/B+树'),
    (45,'算法',        '计算机基础', '排序、搜索、DP、贪心、回溯、双指针、滑动窗口'),
    (46,'设计模式',    '计算机基础', 'GoF 23 种模式、SOLID、架构模式、DDD 基础'),
    (47,'计算机网络',  '计算机基础', 'TCP/IP、HTTP、DNS、CDN、WebSocket、OSI 模型'),
    (48,'操作系统',    '计算机基础', '进程/线程、内存管理、IO多路复用、死锁'),
    (49,'HTTP/HTTPS',  '计算机基础', 'HTTP/1.1 vs /2 vs /3、HTTPS 握手、缓存策略、CORS'),

    # 工程实践
    (50,'Git',         '工程实践', 'Git 分支模型、rebase/merge、cherry-pick、Hook'),
    (51,'CI/CD',       '工程实践', 'Jenkins/GitHub Actions、流水线、自动化部署'),
    (52,'微服务',      '工程实践', '微服务拆分、服务间通信、分布式事务、可观测性'),
    (53,'分布式系统',  '工程实践', 'CAP/BASE、Raft/Paxos、分布式事务、限流熔断'),
    (54,'软件测试',    '工程实践', '单元测试、Mock、集成测试、E2E、TDD、覆盖率'),
    (55,'系统设计',    '工程实践', '高并发架构、数据库扩展、缓存、消息队列应用'),
    (56,'RESTful API', '工程实践', 'REST 设计原则、版本管理、Swagger 文档'),
    (57,'软件工程',    '工程实践', '敏捷、Scrum、需求分析、UML、代码审查'),
]

# ========== 题目数据 (content, reference_answer, answer_keywords, difficulty, followup_guide, [tag_ids]) ==========
# tag_ids 中题目会关联的标签ID
QUESTIONS = [
    # ────────────────── Java 核心 ──────────────────
    {
        "content": "请谈谈 Java 中 == 和 equals() 的区别，以及为什么重写 equals 时必须重写 hashCode？",
        "answer": "== 比较的是栈中的引用地址（基本类型比较值），equals() 在 Object 中默认用 == 比较，子类（如 String）会重写为值比较。重写 equals 必须重写 hashCode 是因为 Java 规范要求：两个对象 equals 相等则 hashCode 必须相等，否则在 HashMap/HashSet 等哈希容器中会出现 key 重复或查找不到的问题。例如：同一个逻辑 key 因为 hashCode 不同落在不同桶中，导致 HashMap 无法正确通过 key 取值。hashCode 的默认实现（native）返回对象内存地址的某种转换，不保证逻辑一致性。",
        "keywords": "引用比较、值比较、Object默认实现、哈希一致性、equals相等则hashCode必须相等、HashMap查找异常",
        "diff": 1,
        "followup": "能举一个不重写 hashCode 导致 HashMap 行为异常的具体例子吗？",
        "tags": [1, 20, 44]
    },
    {
        "content": "说说 Java 的基本数据类型有哪些，以及自动装箱/拆箱可能带来的问题。",
        "answer": "八种基本类型：byte、short、int、long、float、double、char、boolean。对应的包装类：Byte、Short、Integer、Long、Float、Double、Character、Boolean。自动装箱指编译器自动将基本类型转为包装类（Integer i = 10），自动拆箱反之（int j = i）。常见问题：(1) 包装类可为 null，自动拆箱时 NPE（如 Integer i = null; int j = i; 抛 NPE）；(2) 装箱会创建对象，频繁装箱有性能开销；(3) Integer 缓存池 -128 ~ 127，超出范围的 == 比较返回 false（== 比较引用，equals 比较值）；(4) 集合类只能存对象，基本类型会被自动装箱。",
        "keywords": "八种基本类型、包装类、装箱、拆箱、缓存池-128到127、空指针NPE、性能开销、==与equals",
        "diff": 1,
        "followup": "Integer 缓存范围可以调整吗？怎么通过 JVM 参数扩大？",
        "tags": [1, 11]
    },
    {
        "content": "请详解 Java 中 String 的不可变性及其设计原因。",
        "answer": "String 被声明为 final class，内部用 final char[]（JDK 8）或 final byte[]（JDK 9+）存储，没有任何修改方法。设计原因：(1) 字符串常量池复用——字面量相同的字符串指向同一对象，节省内存；(2) 安全性——String 广泛用于类名、文件路径、数据库连接等场景，不可变防止被恶意篡改；(3) 线程安全——不可变对象天然线程安全，无需同步；(4) HashMap 的 key——不可变保证 hashCode 不变，否则存进去就找不到了。实现细节：String 的 concat、replace、substring 等方法都返回新对象，不修改原对象。",
        "keywords": "final class、final byte[]、不可变、字符串常量池、线程安全、HashMap key、新对象",
        "diff": 2,
        "followup": "StringBuilder 和 StringBuffer 的区别是什么？底层如何扩容？",
        "tags": [1, 19]
    },
    {
        "content": "谈谈 Java 的异常体系：Error、Exception、RuntimeException 的区别和各自典型例子。",
        "answer": "Throwable 是根类，下分 Error 和 Exception。(1) Error：JVM 级别的严重错误，程序无法处理也无需处理，如 OutOfMemoryError、StackOverflowError、NoClassDefFoundError。(2) Exception：程序可以捕获处理的异常，分为两类：(a) 受检异常 Checked Exception——编译器强制要求 try-catch 或 throws 声明，如 IOException、SQLException、FileNotFoundException；(b) 非受检异常 RuntimeException——编译器不强制处理，通常是编程错误，如 NullPointerException、IndexOutOfBoundsException、IllegalArgumentException、ClassCastException。最佳实践：不要捕获 Error；受检异常要合理处理而非空 catch；避免用异常控制业务流程。",
        "keywords": "Error、Exception、RuntimeException、Checked Exception、Throwable、NPE、OOM",
        "diff": 1,
        "followup": "try-catch-finally 中 finally 一定会执行吗？什么情况下不会？",
        "tags": [1]
    },
    {
        "content": "说说 Java 中 static 关键字的用法，包括静态内部类和非静态内部类的区别。",
        "answer": "static 可修饰：(1) 变量——类变量，所有实例共享，在类加载时初始化，通过类名访问；(2) 方法——类方法，不能访问非静态成员，没有 this 引用；(3) 代码块——类加载时执行一次，用于静态成员初始化；(4) 内部类——静态内部类不持有外部类引用，可独立创建；非静态内部类隐式持有外部类 this，必须通过外部类实例创建。静态内部类常用于：Builder 模式、工具类辅助类、LazyHolder 单例模式（利用类加载机制保证线程安全）。非静态内部类可能导致内存泄漏——内部类持有外部引用，若外部类本应被 GC 但因内部类被引用而无法回收。",
        "keywords": "类变量、共享、类加载、static block、静态内部类不持有外部引用、内存泄漏、LazyHolder单例",
        "diff": 2,
        "followup": "LazyHolder 单例模式为什么是线程安全的？不用 synchronized 也能安全？",
        "tags": [1, 46]
    },
    {
        "content": "Java 中如何正确比较两个对象？Comparable 和 Comparator 有什么不同？",
        "answer": "对象比较分为自然排序和自定义排序。(1) Comparable 接口：实现 compareTo(Object o) 方法，定义自然排序规则，在类内部实现，如 String、Integer 都实现了 Comparable，TreeSet/TreeMap 默认按此排序。(2) Comparator 接口：实现 compare(Object o1, Object o2) 方法，在类外部定义排序规则，更灵活——可定义多个不同比较器、可按不同字段排序、可对第三方类排序。(3) 比较规则：返回负数表示 o1 < o2，零表示相等，正数表示 o1 > o2。(4) 排序稳定性：Arrays.sort 对对象用 TimSort（稳定），对基本类型用双轴快排（不稳定）。注意事项：compareTo 和 equals 应保持一致（推荐但不强制）。",
        "keywords": "Comparable、compareTo自然排序、Comparator、compare自定义排序、TreeSet、TimSort",
        "diff": 2,
        "followup": "TreeSet 判断元素是否重复是依据 compareTo 还是 equals？",
        "tags": [1]
    },
    {
        "content": "谈谈 Java 反射机制的原理和应用场景，以及它的缺点。",
        "answer": "反射允许程序在运行时获取类的完整信息并操作对象。核心 API：Class.forName() 获取类对象、getDeclaredFields()/getDeclaredMethods() 获取成员、newInstance() 创建实例、Method.invoke() 调用方法、Field.set() 修改属性、setAccessible(true) 绕过访问控制。应用场景：(1) 框架底层——Spring IoC 通过反射实例化 Bean 并注入依赖；(2) ORM——MyBatis/Hibernate 通过反射将 ResultSet 映射到 POJO；(3) 序列化——JSON 序列化库用反射获取属性；(4) 动态代理——JDK 动态代理依赖反射。缺点：(1) 性能开销——反射调用比直接调用慢很多（虽然 JDK 高版本有所优化）；(2) 破坏封装——绕过访问控制；(3) 编译期类型安全检查失效；(4) 代码可读性差。",
        "keywords": "运行时获取类信息、Class.forName、Method.invoke、Field.set、Spring IoC、ORM映射、性能开销、破坏封装",
        "diff": 2,
        "followup": "反射调用的性能开销主要在哪几方面？JDK 是怎么优化的？",
        "tags": [1, 12]
    },
    {
        "content": "Java 的动态代理有几种？分别适用于什么场景？",
        "answer": "两种动态代理：(1) JDK 动态代理——基于接口，通过 Proxy.newProxyInstance() 创建代理对象，InvocationHandler 负责拦截处理，要求目标类必须实现接口。底层原理：运行时动态生成字节码（$Proxy0 类），该类继承 Proxy 并实现所有目标接口。(2) CGLIB 动态代理——基于继承，通过 Enhancer 创建目标类的子类作为代理，MethodInterceptor 拦截方法调用，不要求接口。底层用 ASM 字节码框架动态生成子类。适用场景：JDK 代理适合面向接口编程（Spring AOP 默认优先 JDK 代理）；CGLIB 适合没有接口的类（Spring 在目标类无接口时自动切换 CGLIB）。局限：JDK 只能代理接口方法；CGLIB 不能代理 final 类/final 方法。Spring Boot 2.x+ 默认使用 CGLIB。",
        "keywords": "JDK动态代理、Proxy、InvocationHandler、CGLIB、Enhancer、MethodInterceptor、ASM字节码、final类限制",
        "diff": 3,
        "followup": "Spring AOP 什么时候用 JDK 代理，什么时候用 CGLIB？可以手动指定吗？",
        "tags": [1, 12, 46]
    },

    # ────────────────── JVM ──────────────────
    {
        "content": "请描述 JVM 的内存区域划分，哪些区域是线程私有的？哪些是线程共享的？",
        "answer": "JVM 内存分为：(1) 线程私有区域——程序计数器(PC Register)：指向当前线程执行的字节码行号；虚拟机栈(VM Stack)：每个方法执行时创建栈帧，存储局部变量表、操作数栈、动态链接、返回值；本地方法栈(Native Method Stack)：为 Native 方法服务。(2) 线程共享区域——堆(Heap)：存放对象实例和数组，GC 主要区域，分为新生代(Eden+S0+S1)和老年代；方法区(Method Area / MetaSpace)：存储类信息、常量、静态变量、JIT 编译后的代码缓存。JDK 8+ 用 MetaSpace（本地内存）替代永久代（堆内存），避免 PermGen OOM。直接内存(Direct Memory)：NIO 的 DirectByteBuffer 使用，不在 JVM 堆内但受 JVM 管理。",
        "keywords": "程序计数器、虚拟机栈、本地方法栈、堆、方法区、MetaSpace、线程私有、线程共享、新生代、老年代",
        "diff": 2,
        "followup": "JDK 8 为什么用 MetaSpace 替代永久代？MetaSpace 会 OOM 吗？",
        "tags": [1, 11]
    },
    {
        "content": "请详细说明 JVM 的类加载机制，包括双亲委派模型及其破坏场景。",
        "answer": "类加载分为 5 个阶段：加载→验证→准备→解析→初始化。(1) 加载：通过全限定名获取二进制字节流，转为方法区数据结构，生成 Class 对象。(2) 验证：文件格式、元数据、字节码、符号引用验证。(3) 准备：为静态变量分配内存并赋零值（final static 直接赋值）。(4) 解析：符号引用替换为直接引用。(5) 初始化：执行类构造器 <clinit>()，静态变量赋值和静态代码块。类加载器层级：Bootstrap ClassLoader（加载 rt.jar）→ Extension ClassLoader（jre/lib/ext）→ Application ClassLoader（classpath）。双亲委派模型：每个类加载器先委托父加载器加载，父加载器找不到才自己加载，防止核心类被篡改。破坏场景：(1) JDBC——通过 Thread Context ClassLoader 加载 SPI 实现；(2) Tomcat——每个 WebApp 用独立 ClassLoader 隔离应用；(3) OSGi——网状加载结构。",
        "keywords": "加载、验证、准备、解析、初始化、双亲委派、Bootstrap、Extension、Application、破坏双亲委派、SPI",
        "diff": 3,
        "followup": "Tomcat 为什么要打破双亲委派？不同 Web 应用之间如何做到类隔离？",
        "tags": [1, 11]
    },
    {
        "content": "请比较 JVM 的几种垃圾回收算法：标记-清除、标记-复制、标记-整理，各自优劣？",
        "answer": "(1) 标记-清除(Mark-Sweep)：标记存活对象→清除未标记对象。优点：简单、不需要移动对象。缺点：产生内存碎片，碎片过多可能触发 Full GC；两次扫描效率较低。(2) 标记-复制(Mark-Copy)：将内存分为两块，标记存活对象→复制到另一块→清空当前块。优点：无碎片、分配效率高（指针碰撞）。缺点：可用内存减半。适合新生代——对象死亡率高，只需复制少量存活对象。HotSpot 按 8:1:1 划分 Eden:S0:S1（因为 98% 对象朝生夕死）。(3) 标记-整理(Mark-Compact)：标记存活对象→移动到内存一端→清理边界外内存。优点：无碎片、内存利用率高。缺点：移动对象需要 STW、更新引用开销大。适合老年代——对象存活率高，不适合复制。实际 GC 组合：新生代用复制（ParNew/Parallel Scavenge），老年代用标记-清除-整理（CMS/G1）。",
        "keywords": "标记清除、内存碎片、标记复制、Eden、Survivor、8:1:1、标记整理、STW、新生代、老年代",
        "diff": 2,
        "followup": "G1 收集器是如何兼顾低延迟和高吞吐的？Region 的设计解决了什么痛点？",
        "tags": [11, 1]
    },
    {
        "content": "什么情况会触发 Full GC？如何通过 JVM 参数和工具进行 GC 调优？",
        "answer": "触发 Full GC 的场景：(1) System.gc() 显式调用（建议 JVM 执行，不保证）；(2) 老年代空间不足（新生代对象晋升/大对象直接分配老年代）；(3) MetaSpace 空间不足；(4) 担保失败——老年代剩余空间 < 新生代所有对象大小之和；(5) CMS 并发失败（Concurrent Mode Failure）——用户线程和 GC 线程并发时老年代填满。GC 调优方法：(1) 选合适的收集器——低延迟用 G1/ZGC，高吞吐用 Parallel，大堆用 G1；(2) 调整堆大小 -Xms/-Xmx 设为相同值避免动态扩展；(3) 调整新生代比例 -XX:NewRatio；(4) 设置关键阈值 -XX:MaxTenuringThreshold、-XX:SurvivorRatio 等；(5) 使用 jstat -gc、GC 日志（-Xlog:gc*）、Arthas、VisualVM、MAT 分析。调优目标：减少 Full GC 次数、缩短 STW 时间。",
        "keywords": "老年代不足、MetaSpace不足、担保失败、CMS并发失败、G1、ZGC、-Xms、-Xmx、GC日志、jstat",
        "diff": 3,
        "followup": "你的项目中实际调过 GC 参数吗？怎么做 GC 日志分析的？",
        "tags": [11, 1]
    },

    # ────────────────── Spring / Spring Boot ──────────────────
    {
        "content": "请详细说明 Spring 的 IoC 容器和依赖注入(DI)的原理。",
        "answer": "IoC（控制反转）是将对象创建和依赖管理的控制权从程序代码反转到 Spring 容器。DI（依赖注入）是 IoC 的具体实现方式。Spring IoC 容器核心是 BeanFactory（基础容器）和 ApplicationContext（高级容器，增加国际化、事件发布、AOP 等）。DI 三种方式：(1) 构造器注入（@Autowired 在构造器）——推荐，保证依赖不可变、不依赖反射；(2) Setter 注入——可选依赖，允许运行时修改；(3) 字段注入（@Autowired 在字段）——简洁但难以测试（需反射注入）、隐藏依赖细节。容器启动流程：解析配置（XML/注解/Java Config）→ BeanDefinition 注册 → BeanFactoryPostProcessor 处理 → Bean 实例化 → 属性填充 → Aware 回调 → BeanPostProcessor 前置处理 → 初始化 → BeanPostProcessor 后置处理 → Bean 就绪。三级缓存解决循环依赖。",
        "keywords": "IoC控制反转、DI依赖注入、BeanFactory、ApplicationContext、构造器注入、BeanPostProcessor、三级缓存",
        "diff": 2,
        "followup": "构造器注入 vs 字段注入，Spring 官方推荐哪种？为什么？",
        "tags": [12, 13]
    },
    {
        "content": "Spring AOP 的实现原理是什么？JDK 代理和 CGLIB 代理如何选择？",
        "answer": "AOP（面向切面编程）通过动态代理实现横切关注点的模块化。(1) JDK 动态代理：基于接口，目标类必须有接口。Proxy.newProxyInstance() 生成代理对象，InvocationHandler 拦截方法。Spring AOP 默认优先用 JDK 代理。(2) CGLIB 代理：基于继承，生成目标类的子类，MethodInterceptor 拦截。不需接口，但不能代理 final 类/方法。Spring Boot 2.x 默认 CGLIB（proxy-target-class=true）。AOP 核心概念：Aspect（切面）、JoinPoint（连接点）、Advice（通知类型：@Before/@After/@Around/@AfterReturning/@AfterThrowing）、Pointcut（切入点表达式）。执行顺序：Around 前 → Before → 目标方法 → Around 后 → After → AfterReturning（正常）/ AfterThrowing（异常）。注意：同一个类内方法调用不会触发 AOP（this.method() 绕过代理）。",
        "keywords": "AOP、动态代理、JDK代理、CGLIB、Aspect、Advice、Pointcut、@Around环绕通知、内部调用不触发代理",
        "diff": 3,
        "followup": "同一个类中方法 A 调用方法 B，为什么 B 上的 @Transactional 不生效？怎么解决？",
        "tags": [12, 13, 1]
    },
    {
        "content": "Spring Boot 自动配置原理是什么？如何自定义一个 Starter？",
        "answer": "自动配置核心流程：(1) @SpringBootApplication 包含 @EnableAutoConfiguration；(2) @EnableAutoConfiguration 通过 @Import(AutoConfigurationImportSelector.class) 导入自动配置类；(3) AutoConfigurationImportSelector 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports 文件（Spring Boot 3.x），加载所有自动配置类；(4) 每个自动配置类用 @ConditionalOnClass/@ConditionalOnBean/@ConditionalOnProperty 等条件注解判断是否生效；(5) 满足条件则创建 Bean。自定义 Starter：(1) 创建 autoconfigure 模块——编写自动配置类（@Configuration + @ConditionalOnXxx），在 META-INF/spring/...autoConfiguration.imports 中注册；(2) 创建 starter 模块——空模块，只引入 autoconfigure 和所需依赖；(3) 用 @ConfigurationProperties 暴露配置属性；(4) 发布到 Maven 仓库。",
        "keywords": "@EnableAutoConfiguration、AutoConfigurationImportSelector、spring.factories、条件注解@ConditionalOnClass、自定义Starter、自动配置类",
        "diff": 3,
        "followup": "@ConditionalOnMissingBean 和 @ConditionalOnBean 怎么配合使用？有什么坑？",
        "tags": [13, 12]
    },
    {
        "content": "Spring 声明式事务 @Transactional 的原理、失效场景及解决方法。",
        "answer": "原理：@Transactional 通过 AOP 在方法前后开启/提交/回滚事务。核心是 PlatformTransactionManager，DataSourceTransactionManager（JDBC/MyBatis）或 JpaTransactionManager（JPA）管理连接与事务。事务传播行为（Propagation）：REQUIRED（默认，有则加入无则新建）、REQUIRES_NEW（挂起当前事务新开）、NESTED（嵌套保存点）等。失效场景：(1) 同类方法调用（this.method() 绕过代理）；(2) 方法非 public（CGLIB 只能代理 public 方法）；(3) 异常被 catch 吃掉未抛出；(4) rollbackFor 未包含实际异常类型（默认只回滚 RuntimeException 和 Error）；(5) 数据库引擎不支持事务（MyISAM）；(6) 多线程——每个线程独立事务。解决：同类调用通过 AopContext.currentProxy() 获取代理；指定 rollbackFor = Exception.class；使用编程式事务 TransactionTemplate。",
        "keywords": "@Transactional、AOP、REQUIRED、REQUIRES_NEW、同类调用失效、非public、rollbackFor、TransactionTemplate",
        "diff": 2,
        "followup": "REQUIRED 和 REQUIRES_NEW 在什么场景下分别使用？REQUIRES_NEW 有什么风险？",
        "tags": [12, 13, 15]
    },
    {
        "content": "谈谈 Spring Bean 的几种作用域，以及各自的生命周期和应用场景。",
        "answer": "Spring Bean 作用域：(1) singleton（默认）：整个 IoC 容器只有一个实例，容器启动时默认创建（急加载），也可 @Lazy 延迟加载。适用：无状态 Service、DAO、工具类。(2) prototype：每次请求获取新实例，容器仅负责创建，不管理完整生命周期（不调用 destroy 回调）。适用：有状态的 Bean、每次使用需独立实例。(3) request：每个 HTTP 请求一个实例（仅 Web 环境），请求结束销毁。(4) session：每个 HTTP Session 一个实例。(5) application：全局唯一（ServletContext 级别）。(6) websocket：每个 WebSocket 连接一个实例。(7) 自定义 scope——实现 Scope 接口。注意：singleton 注入 prototype 时，prototype 也成了单例——因为 singleton 只创建一次，其依赖也只注入一次。解决：@Lookup 方法注入或注入 ObjectFactory。",
        "keywords": "singleton、prototype、单例、@Lazy、@Lookup方法注入、ObjectFactory、singleton注入prototype问题",
        "diff": 2,
        "followup": "为什么 singleton 类型的 Bean 是线程安全的？不安全的场景在哪？",
        "tags": [12, 13]
    },
    {
        "content": "Spring MVC 的 DispatcherServlet 处理请求的完整流程是怎样的？",
        "answer": "流程：(1) 客户端请求到达 DispatcherServlet（前端控制器）；(2) DispatcherServlet 调用 HandlerMapping 查找处理器（根据 URL/请求方式等），返回 HandlerExecutionChain（包含 Handler + 拦截器列表）；(3) DispatcherServlet 调用 HandlerAdapter，适配不同类型的 Handler（如 @Controller 的方法、HttpRequestHandler 等）；(4) HandlerAdapter 执行前置拦截器（preHandle）→ 调用 Handler（即 Controller 方法）→ 后置拦截器（postHandle）；(5) Handler 返回 ModelAndView（或 @ResponseBody 时直接写响应）；(6) DispatcherServlet 调用 ViewResolver 将逻辑视图名解析为具体 View；(7) View 渲染 Model 数据生成 HTML 响应；(8) 完成拦截器（afterCompletion）。若使用 @RestController/@ResponseBody，第(6)-(7)步替换为 HttpMessageConverter 将返回值序列化为 JSON/XML。",
        "keywords": "DispatcherServlet、HandlerMapping、HandlerAdapter、HandlerExecutionChain、拦截器、ViewResolver、HttpMessageConverter",
        "diff": 2,
        "followup": "Spring MVC 拦截器和 Filter 有什么区别？执行顺序是怎样的？",
        "tags": [12, 13]
    },
    {
        "content": "MyBatis 中 #{} 和 ${} 的区别是什么？为什么 SQL 注入是 ${} 的问题？",
        "answer": "#{} 是预编译占位符，MyBatis 会将 SQL 中的 #{} 替换为 ?，然后通过 PreparedStatement 的 setXxx() 方法设置参数值。好处：(1) 防止 SQL 注入——参数值被当作数据而非 SQL 片段；(2) 预编译提升性能——同一条 SQL 只需编译一次（需数据库和驱动支持）；(3) 自动类型转换和转义。${} 是字符串替换，MyBatis 直接将参数值拼接进 SQL 字符串（类似字符串拼接），然后整体发送给数据库。风险：(1) SQL 注入——恶意输入可修改 SQL 语义（如传入 ' OR '1'='1）；(2) 无法预编译。${} 的合法场景：(1) 动态表名/列名（如分表 order_${year}）；(2) ORDER BY ${column}——排序字段名不能预编译；(3) 动态 GROUP BY。使用 ${} 时必须做白名单校验。",
        "keywords": "#{}预编译、PreparedStatement、?占位符、防SQL注入、${}字符串替换、动态表名、白名单校验",
        "diff": 1,
        "followup": "如果必须用 ${} 做动态排序，你怎么确保安全？",
        "tags": [15, 26, 1]
    },
    {
        "content": "MyBatis 的一级缓存和二级缓存有什么区别？各自的使用注意事项是什么？",
        "answer": "一级缓存（SqlSession 级别）：默认开启，同一 SqlSession 内相同查询只执行一次 SQL，后续从缓存取。生命周期跟随 SqlSession，commit/close/clearCache 时清空。注意：不同 SqlSession 间缓存不共享，数据变更后缓存可能脏读。二级缓存（Mapper/Namespace 级别）：需显式配置——mapper.xml 中加 <cache/> 标签，实体类实现 Serializable。同一 namespace 内、不同 SqlSession 间共享。工作流程：先查二级缓存→再查一级缓存→最后查数据库。注意事项：(1) 只有 commit 后数据才进入二级缓存；(2) 多表关联查询易产生脏数据——一个表的更新不会清空另一个表的缓存；(3) 分布式环境需借助 Redis 等外部缓存；(4) 不适合频繁更新的数据。MyBatis-Plus 在此基础上提供了更便捷的注解缓存支持。",
        "keywords": "一级缓存、SqlSession、二级缓存、namespace、cache标签、Serializable、脏数据、Redis外部缓存",
        "diff": 2,
        "followup": "在生产环境中你更倾向于用 MyBatis 二级缓存还是 Redis？为什么？",
        "tags": [15, 22]
    },

    # ────────────────── MySQL ──────────────────
    {
        "content": "MySQL 的 InnoDB 存储引擎中 B+Tree 索引原理，为什么不用 B-Tree 或二叉树？",
        "answer": "B+Tree 特点：(1) 所有数据存储在叶子节点，非叶子节点只存索引 key，一个节点可存更多 key→树更矮→IO 次数少；(2) 叶子节点通过双向链表连接，支持高效的范围查询（ORDER BY / BETWEEN / >）；(3) 数据按索引顺序存储，天然有序。vs B-Tree：B-Tree 非叶子节点也存数据，单个节点存 key 少→树更高→IO 多；范围查询需要中序遍历效率低。vs 二叉树：二叉树在极端情况（有序插入）退化为链表→O(n)；平衡二叉树每个节点只有两个子节点→树高度大→磁盘 IO 多。B+Tree 一个节点（默认 16KB 页）可存约 1170 个 key，3 层即可索引约 2000 万行数据，查找仅需 3 次 IO。聚簇索引(主键索引)叶子存完整行数据；二级索引叶子存主键值，查询需要回表。",
        "keywords": "B+Tree、叶子节点存数据、非叶子存索引、双向链表、范围查询、三级2000万行、聚簇索引、二级索引、回表",
        "diff": 2,
        "followup": "什么是覆盖索引？如何利用覆盖索引避免回表？",
        "tags": [20, 26, 44]
    },
    {
        "content": "MySQL 的四种事务隔离级别分别是什么？各自解决/未解决什么问题？InnoDB 默认用什么？",
        "answer": "(1) READ UNCOMMITTED（读未提交）：允许读未提交数据，存在脏读、不可重复读、幻读。(2) READ COMMITTED（读已提交）：只读已提交数据，解决脏读；存在不可重复读、幻读。每次快照读都生成新 ReadView。(3) REPEATABLE READ（可重复读）：同一事务内多次读取结果一致，解决脏读和不可重复读；InnoDB 通过间隙锁(Gap Lock)在一定程度上解决幻读，但非完全（如 SELECT ... FOR UPDATE 范围的插入仍可能幻读）。每次事务使用同一个 ReadView。(4) SERIALIZABLE（串行化）：所有读加共享锁，写加排他锁，完全串行执行——解决所有问题但性能最差。InnoDB 默认为 REPEATABLE READ。MVCC 利用 Undo Log 和 ReadView 实现非锁定一致性读，是隔离级别的底层支撑。",
        "keywords": "读未提交、读已提交、可重复读、串行化、脏读、不可重复读、幻读、间隙锁、MVCC、ReadView、Undo Log",
        "diff": 3,
        "followup": "为什么 Oracle 和 PostgreSQL 默认用 READ COMMITTED，而 MySQL InnoDB 用 RR？",
        "tags": [20, 26]
    },
    {
        "content": "什么是 MySQL 的慢查询？如何定位和优化一条慢 SQL？",
        "answer": "慢查询：执行时间超过 long_query_time（默认 10s）的 SQL。定位方法：(1) 开启 slow_query_log，分析慢查询日志（mysqldumpslow 工具）；(2) 使用 EXPLAIN 分析执行计划：关注 type（const>eq_ref>ref>range>index>ALL）、key（使用的索引）、rows（扫描行数）、Extra（Using filesort/Using temporary 是危险信号）；(3) Performance Schema 监控实时 SQL；(4) 第三方工具（pt-query-digest、DBA 平台）。优化方法：(1) 加索引——WHERE/JOIN/ORDER BY 字段建联合索引，遵循最左前缀原则；(2) 覆盖索引避免回表；(3) 减少返回数据量——SELECT 指定字段不用 *，分页用 LIMIT；(4) 避免索引失效——不用函数包裹索引列、避免隐式类型转换、OR 条件拆分；(5) 大表分库分表；(6) SQL 重写——用 JOIN 替代子查询、IN 拆分等；(7) 读写分离。",
        "keywords": "slow_query_log、EXPLAIN、type、key、rows、Extra、最左前缀、覆盖索引、索引失效、mysqldumpslow",
        "diff": 2,
        "followup": "EXPLAIN 执行计划中 Using filesort 是怎么回事？如何消除？",
        "tags": [20, 26]
    },
    {
        "content": "MySQL 中 varchar 和 char 的区别？int(11) 中的 11 是什么意思？",
        "answer": "varchar vs char：(1) varchar：变长字符串，只占用实际数据长度+1~2字节（长度前缀），最大 65535 字节（受行大小和编码影响），适合长度变化大的字段（姓名、地址）；(2) char：定长字符串，始终占用声明长度，最大 255 字符，读写效率高（不用计算长度），适合长度固定的字段（手机号、MD5、UUID）。int(11) 中的 11 是显示宽度（display width），不是存储范围——int 固定占 4 字节，范围始终是 -2^31 ~ 2^31-1。11 只在搭配 ZEROFILL 时有效（左边补零到 11 位）。MySQL 8.0.17+ 已废弃 int(N) 语法（除 tinyint(1) 表示 BOOL 外）。选型建议：金额用 DECIMAL（避免浮点误差）、状态用 TINYINT、时间用 DATETIME（比 TIMESTAMP 范围大，不依赖时区）、长文本用 TEXT/LONGTEXT。",
        "keywords": "varchar变长、char定长、65535字节限制、int(11)显示宽度、ZEROFILL补零、DECIMAL金额、DATETIME范围",
        "diff": 1,
        "followup": "UTF-8 和 UTF8MB4 的区别是什么？emoji 应该用什么编码？",
        "tags": [20, 26]
    },

    # ────────────────── Redis ──────────────────
    {
        "content": "Redis 的五种基本数据类型及各自典型的应用场景是什么？",
        "answer": "(1) String：SET/GET 操作，底层 SDS（简单动态字符串）。场景：缓存（JSON 序列化后存）、计数器（INCR 原子自增）、分布式锁（SETNX+过期时间）、限流（滑动窗口计数器）。(2) Hash：HMSET/HGETALL，底层 ziplist/hashtable。场景：对象存储（用户信息、商品详情），比 String 存 JSON 更节省空间且可部分更新。(3) List：LPUSH/RPOP，底层 quicklist（linkedlist+ziplist 混合）。场景：消息队列（BRPOP 阻塞读）、最新 N 条记录（LPUSH+ LTRIM 控制长度）、时间线。(4) Set：SADD/SINTER/SUNION，底层 inset/hashtable。场景：标签、共同好友（交集）、抽奖去重、UV 统计。(5) ZSet：ZADD/ZRANGEBYSCORE，底层 skiplist+hashtable。场景：排行榜（按 score 排序）、延迟队列（score=执行时间戳）、带权重的标签。此外还有 Bitmap（签到）、HyperLogLog（UV 统计误差 0.81%）、Geo（附近的人）、Stream（持久化消息队列）。",
        "keywords": "String、Hash、List、Set、ZSet、SDS、quicklist、skiplist、分布式锁、排行榜、延迟队列",
        "diff": 2,
        "followup": "ZSet 底层为什么用跳表而不用红黑树？跳表有什么优势？",
        "tags": [22, 44]
    },
    {
        "content": "请解释 Redis 缓存穿透、缓存击穿、缓存雪崩的区别和各自的解决方案。",
        "answer": "缓存穿透：查询一个数据库中根本不存在的数据（如查询 id=-1），缓存和 DB 都没有，大量此类请求直接打到 DB。解决：(1) 布隆过滤器——用极小内存判断 key 是否可能存在（一定不存在 / 可能存在）；(2) 缓存空值——将 null 也缓存，设置短过期时间（如 5 分钟）；(3) 前端参数校验过滤非法请求。缓存击穿：热点 key 在过期瞬间，大量并发请求同时打到 DB。解决：(1) 互斥锁——第一个请求获取锁后查 DB 并回写缓存，其余等待（SETNX 或 Redisson 分布式锁）；(2) 逻辑过期——缓存永不过期，另起线程异步更新（适合对一致性要求不高的热点数据）；(3) 热点 key 永不过期。缓存雪崩：大量 key 同时过期（如缓存预热时设置了相同的过期时间），或 Redis 宕机。解决：(1) 过期时间加随机值（±30% 打散）；(2) Redis 高可用——主从+哨兵/集群；(3) 多级缓存——本地缓存(Caffeine) + Redis；(4) 限流降级——sentinel 限流保护 DB。",
        "keywords": "缓存穿透、布隆过滤器、缓存空值、缓存击穿、互斥锁、逻辑过期、缓存雪崩、过期时间打散、多级缓存",
        "diff": 3,
        "followup": "布隆过滤器的原理是什么？为什么它会有误判？误判率怎么计算？",
        "tags": [22, 53]
    },
    {
        "content": "Redis 持久化的两种方式 RDB 和 AOF 有什么区别？如何选择？",
        "answer": "RDB（快照）：定期将内存数据快照保存为 dump.rdb 二进制文件。触发方式：SAVE（阻塞主线程）/ BGSAVE（fork 子进程后台写）/ 配置 save 900 1 等条件自动触发。优点：文件紧凑、恢复快、fork 子进程写时不阻塞主线程、适合备份和灾难恢复。缺点：两次快照间的数据可能丢失（非实时）、fork 子进程耗时（大内存可能秒级阻塞）、老版本 Redis 在写时复制期间内存翻倍。AOF（追加文件）：将每条写命令追加到 appendonly.aof 文件。fsync 策略：always（每次命令都刷盘，最安全最慢）/ everysec（每秒刷盘，折中）/ no（OS 决定）。优点：数据安全性高（最多丢 1 秒数据）、文件可读（可手动修复）、AOF 重写（压缩冗余命令）。缺点：AOF 文件通常比 RDB 大、恢复速度比 RDB 慢。推荐：生产环境同时开启（Redis 重启优先加载 AOF），RDB 做定期备份，AOF 保证数据安全。混合持久化（Redis 4.0+）：AOF 重写时将 RDB 二进制内容写入 AOF 头部，兼顾恢复速度和数据安全。",
        "keywords": "RDB快照、BGSAVE、fork子进程、AOF追加、always、everysec、fsync、AOF重写、混合持久化",
        "diff": 2,
        "followup": "AOF 重写机制的原理是什么？重写过程中新写入的数据怎么处理？",
        "tags": [22]
    },
    {
        "content": "如何用 Redis 实现分布式锁？Redisson 的看门狗机制解决了什么问题？",
        "answer": "基础实现：SET key value NX EX timeout——原子操作同时设置锁和过期时间，防止死锁。value 用 UUID+线程ID，释放时 Lua 脚本判断 value 一致性（防止释放别人的锁）。问题+解决：(1) 锁过期任务未完成——看门狗(Watchdog)：Redisson 每 10 秒自动续期 30 秒，任务完成后停止续期。(2) 主从切换锁丢失——RedLock 算法：向 N 个独立 Redis 节点（非主从）依次获取锁，超过 N/2+1 成功且总耗时 < 锁有效期才算成功。但 RedLock 有争议（Martin Kleppmann 提出安全性问题）。(3) 性能——单节点分布式锁足够大多数场景，RedLock 只用于对一致性要求极高的场景。(4) 可重入——Redisson 内部用 Hash 结构（hset key threadId 重入次数）支持可重入锁。注意：分布式锁不应依赖过期时间的精确性，业务需幂等设计。",
        "keywords": "SET NX EX、UUID防止误删、Lua脚本原子释放、看门狗续期、RedLock算法、N/2+1、可重入锁",
        "diff": 3,
        "followup": "RedLock 为什么存在争议？什么场景下你才会考虑使用 RedLock？",
        "tags": [22, 53]
    },
    {
        "content": "Redis 集群的几种模式：主从、哨兵、Cluster 各有什么特点？",
        "answer": "(1) 主从复制(Master-Slave)：一主多从，主负责写，从负责读（需客户端或中间件路由）。异步复制，可能丢数据。全量同步(psync)发送 RDB 快照，增量同步(partial sync)发送命令缓冲。适用于：读写分离提升读性能。局限：主节点故障需手动切换。(2) 哨兵(Sentinel)：在主从基础上加哨兵进程——监控节点健康→主节点故障时，Raft 算法选举 Sentinel Leader 执行自动故障转移→选新主→通知客户端。哨兵至少 3 个（防止脑裂），需奇数个。适用于：高可用场景，中小规模数据。(3) Cluster：去中心化分布式——16384 个哈希槽分布在多个节点，客户端按 CRC16(key) % 16384 计算槽位直连对应节点。支持水平扩展（加节点→槽迁移）、自动故障转移（Gossip 协议检测节点状态）。局限：不支持跨槽事务、多 key 操作需在同一槽（用 {} hash tag）、批量操作需客户端支持（如 pipeline 路由）。适用于：海量数据、高吞吐场景。",
        "keywords": "主从复制、哨兵Sentinel、Cluster、16384哈希槽、CRC16、Gossip协议、故障转移、hash tag",
        "diff": 3,
        "followup": "Redis Cluster 的 MOVED 和 ASK 重定向有什么区别？",
        "tags": [22, 53]
    },

    # ────────────────── 计算机网络 ──────────────────
    {
        "content": "TCP 三次握手和四次挥手的过程，为什么握手是三次、挥手是四次？",
        "answer": "三次握手：(1) Client→Server: SYN=1, seq=x（客户端请求建立连接）；(2) Server→Client: SYN=1, ACK=1, seq=y, ack=x+1（服务端确认并请求反向连接）；(3) Client→Server: ACK=1, seq=x+1, ack=y+1（客户端确认，连接建立）。为什么三次而不是两次：防止历史失效的连接请求到达服务端——Client 发了 SYN 但超时重发，旧 SYN 后到，Server 回 SYN+ACK，若只两次握手则 Server 单方面建立连接浪费资源。四次挥手：(1) Client→Server: FIN=1, seq=u（客户端发完数据请求关闭）；(2) Server→Client: ACK=1, ack=u+1（服务端确认收到，此时 TCP 半关闭，Server 可以继续发数据）；(3) Server→Client: FIN=1, ACK=1, seq=w, ack=u+1（服务端数据发完）；(4) Client→Server: ACK=1, ack=w+1，进入 TIME_WAIT 等待 2MSL 后关闭。为什么挥手四次：TCP 全双工，双方都可发数据，服务端收到 FIN 后可能还有数据要发（ACK 和 FIN 分开发）。TIME_WAIT 必要性：(1) 确保最后的 ACK 到达 Server；(2) 让旧连接的残留报文在网络中消失。",
        "keywords": "SYN、ACK、FIN、三次握手、四次挥手、TIME_WAIT、2MSL、全双工、半关闭",
        "diff": 2,
        "followup": "TIME_WAIT 过多会导致什么问题？如何优化（tcp_tw_reuse / tcp_tw_recycle）？",
        "tags": [47, 48]
    },
    {
        "content": "说说 TCP 的拥塞控制算法：慢启动、拥塞避免、快重传、快恢复的过程。",
        "answer": "拥塞控制用拥塞窗口 cwnd 限制发送速率。(1) 慢启动(Slow Start)：初始 cwnd=1 MSS，每收到一个 ACK cwnd+1（指数增长），直到达到慢启动门限 ssthresh。(2) 拥塞避免(Congestion Avoidance)：cwnd >= ssthresh 后，每 RTT cwnd+1（线性增长）。(3) 快重传(Fast Retransmit)：发送方连续收到 3 个重复 ACK（说明中间某个包丢失）→不等超时立刻重传丢失的包。(4) 快恢复(Fast Recovery)：收到 3 个重复 ACK 后——ssthresh=cwnd/2，cwnd=ssthresh+3，进入拥塞避免阶段（不降到慢启动，认为偶尔丢包不代表拥塞严重）。超时重传(RTO)时→ssthresh=cwnd/2，cwnd=1→回到慢启动（认为严重拥塞）。常见拥塞控制算法：Reno（经典）、CUBIC（Linux 默认，三次函数调整窗口）、BBR（Google，基于带宽和 RTT 而非丢包）。",
        "keywords": "cwnd拥塞窗口、慢启动指数增长、ssthresh门限、拥塞避免线性增长、3个重复ACK快重传、快恢复、CUBIC、BBR",
        "diff": 3,
        "followup": "BBR 和 CUBIC 的核心区别是什么？BBR 为什么在丢包率高的链路表现更好？",
        "tags": [47]
    },

    # ────────────────── 剩余题目见 Part2 ──────────────────
]

SQLEOF_END
