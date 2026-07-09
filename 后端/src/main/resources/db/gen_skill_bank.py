#!/usr/bin/env python3
"""一次性从 Python 数据生成 seed_skill_bank.sql"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seed_skill_bank.sql')

# ================================================================
# 57 技能标签
# ================================================================
TAGS = [
    (1,"Java","编程语言","Java核心语法、OOP、集合、泛型、注解、反射、IO/NIO"),
    (2,"C","编程语言","C语言：指针、内存管理、结构体、预处理、文件操作"),
    (3,"C++","编程语言","C++ OOP、STL、智能指针、RAII、C++11/14/17新特性"),
    (4,"Python","编程语言","Python装饰器、生成器、GIL、常用库(numpy/pandas/Django)"),
    (5,"JavaScript","编程语言","JS闭包、原型链、异步编程、ES6+、事件循环"),
    (6,"TypeScript","编程语言","TS类型系统、泛型、工具类型、装饰器"),
    (7,"Go","编程语言","Go goroutine/channel、GMP调度、接口"),
    (8,"Rust","编程语言","Rust所有权、生命周期、trait、unsafe"),
    (9,"Kotlin","编程语言","Kotlin协程、空安全、扩展函数、与Java互操作"),
    (10,"PHP","编程语言","PHP核心、Composer、Laravel/ThinkPHP、FPM"),
    (11,"JVM","Java生态","JVM内存模型、类加载、GC、JIT编译、性能调优"),
    (12,"Spring","Java生态","Spring IoC/AOP、事务管理、Bean生命周期、设计模式"),
    (13,"Spring Boot","Java生态","Spring Boot自动配置、Starter、Actuator、外部化配置"),
    (14,"Spring Cloud","Java生态","微服务治理：服务注册发现、配置中心、网关、熔断降级"),
    (15,"MyBatis","Java生态","MyBatis映射、动态SQL、缓存、插件机制、MyBatis-Plus"),
    (16,"Hibernate","Java生态","Hibernate ORM、JPA规范、缓存、N+1问题、延迟加载"),
    (17,"Maven","Java生态","Maven依赖管理、生命周期、插件机制、多模块构建"),
    (18,"Gradle","Java生态","Gradle构建脚本、Task依赖、插件、增量构建"),
    (19,"Java并发","Java生态","线程池、锁机制、AQS、volatile、原子类、并发集合、ForkJoin"),
    (20,"MySQL","数据库","MySQL索引、事务、锁、MVCC、SQL优化、主从复制、分库分表"),
    (21,"PostgreSQL","数据库","PostgreSQL窗口函数、CTE、JSONB、全文搜索、扩展机制"),
    (22,"Redis","数据库","Redis数据结构、持久化、集群、缓存策略、分布式锁"),
    (23,"MongoDB","数据库","MongoDB文档模型、聚合管道、索引、副本集、分片集群"),
    (24,"Elasticsearch","数据库","ES倒排索引、查询DSL、聚合分析、集群调优"),
    (25,"Oracle","数据库","Oracle体系架构、PL/SQL、分区表、物化视图、RAC"),
    (26,"SQL","数据库","SQL查询优化、复杂联表、子查询、窗口函数、索引设计、执行计划"),
    (27,"Kafka","中间件","Kafka生产消费模型、分区、副本、ISR、幂等、流处理"),
    (28,"RabbitMQ","中间件","RabbitMQ交换机类型、死信队列、延迟队列、消息可靠性"),
    (29,"RocketMQ","中间件","RocketMQ事务消息、顺序消息、延迟消息、NameServer"),
    (30,"Nginx","中间件","Nginx反向代理、负载均衡、动静分离、HTTPS配置、性能调优"),
    (31,"Docker","中间件","Docker镜像构建、Dockerfile、Compose、网络模式、多阶段构建"),
    (32,"Kubernetes","中间件","K8s Pod/Deployment/Service、调度、Helm、Ingress"),
    (33,"Zookeeper","中间件","ZooKeeper数据模型、ZAB协议、Watch机制、选举、分布式锁"),
    (34,"Linux","中间件","Linux常用命令、Shell脚本、文件系统、进程管理、性能分析"),
    (35,"HTML","前端","HTML5语义化标签、表单、Canvas、Web Storage、SEO基础"),
    (36,"CSS","前端","CSS3盒模型、Flex/Grid、动画、响应式、BFC、预处理器"),
    (37,"Vue","前端","Vue3响应式、组合式API、虚拟DOM、diff算法、Router、Pinia"),
    (38,"React","前端","React Hooks、Fiber架构、虚拟DOM、Redux/Zustand、Next.js"),
    (39,"Angular","前端","Angular模块化、依赖注入、RxJS、路由守卫、变更检测"),
    (40,"Webpack","前端","Webpack打包原理、Loader/Plugin、代码分割、TreeShaking、HMR"),
    (41,"Vite","前端","Vite ESBuild预构建、HMR、Rollup打包、SSR"),
    (42,"Element Plus","前端","Element Plus组件库使用、主题定制、表单校验、国际化"),
    (43,"ECharts","前端","ECharts图表配置、数据绑定、交互事件、自适应、性能优化"),
    (44,"数据结构","计算机基础","数组/链表/栈/队列/树/图/哈希表、时间复杂度、B/B+树、跳表"),
    (45,"算法","计算机基础","排序、搜索、DP、贪心、回溯、分治、滑动窗口、双指针"),
    (46,"设计模式","计算机基础","GoF23种设计模式、SOLID原则、常见架构模式、DDD基础"),
    (47,"计算机网络","计算机基础","TCP/IP、HTTP/HTTPS、DNS、CDN、WebSocket、OSI模型"),
    (48,"操作系统","计算机基础","进程/线程、内存管理、文件系统、IO多路复用、死锁、CPU调度"),
    (49,"HTTP/HTTPS","计算机基础","HTTP各版本差异、状态码、缓存策略、HTTPS握手、证书链、CORS"),
    (50,"Git","工程实践","Git分支模型、rebase/merge、cherry-pick、submodule、Hook"),
    (51,"CI/CD","工程实践","Jenkins/GitHub Actions/GitLab CI流水线、自动化测试、部署策略"),
    (52,"微服务","工程实践","微服务拆分原则、服务间通信、分布式事务、可观测性、DDD"),
    (53,"分布式系统","工程实践","CAP理论、BASE、一致性协议(Raft/Paxos)、分布式事务、限流熔断"),
    (54,"软件测试","工程实践","单元测试(JUnit/Jest)、Mock、集成测试、E2E、TDD、测试覆盖率"),
    (55,"系统设计","工程实践","高并发架构设计、数据库扩展、缓存策略、消息队列应用、容量规划"),
    (56,"RESTful API","工程实践","REST设计原则、资源命名、版本管理、Swagger/OpenAPI文档"),
    (57,"软件工程","工程实践","敏捷开发、Scrum/Kanban、需求分析、UML、代码审查、技术债务管理"),
]

# ================================================================
# 题目(面试题) -- (题干, 参考答案, 关键词, 难度1-3, 追问引导, [标签ID列表])
# ================================================================
Q = []

# ---- Java 核心 (tag 1) ----
Q.append(("请谈谈Java中==和equals()的区别，以及为什么重写equals时必须重写hashCode？",
    "==比较栈中引用地址(基本类型比值); equals()在Object中默认用==比较，子类String重写为值比较。重写equals必须重写hashCode是因Java规范要求equals相等的两个对象hashCode必须相等，否则HashMap/HashSet中逻辑相同的key会落在不同桶中导致查找失败。",
    "引用比较、值比较、Object默认实现、哈希一致性、equals相等则hashCode必须相等、HashMap查找失败", 1,
    "能举一个不重写hashCode导致HashMap行为异常的具体例子吗？", [1,20,44]))

Q.append(("Java的基本数据类型有哪些？自动装箱和拆箱可能带来什么问题？",
    "8种:byte/short/int/long/float/double/char/boolean。包装类:Byte/Short/Integer/Long/Float/Double/Character/Boolean。自动装箱如Integer i=10(编译器生成Integer.valueOf(10)); 拆箱如int j=i(生成i.intValue())。问题:(1)包装类为null时拆箱抛NPE; (2)频繁装箱有性能开销; (3)Integer缓存池-128~127超出此范围==比较引用返回false; (4)集合类只能存对象，基本类型自动装箱增加GC压力。",
    "8种基本类型、包装类、装箱拆箱、缓存池128到127、NPE空指针、==与equals", 1,
    "Integer缓存范围可以调整吗？怎么通过JVM参数扩大？", [1,11]))

Q.append(("Java中String为什么设计为不可变？从常量池、安全性和线程安全角度说明。",
    "String是final class，内部final byte[]不可修改。设计原因:(1)字符串常量池——同值字面量指向同一对象，节省堆内存; (2)安全性——String广泛用于类名、文件路径、数据库URL等场景，不可变防止被篡改; (3)线程安全——不可变对象天然线程安全无需同步; (4)作为HashMap key时保证hashCode不变。concat、replace、substring等方法均返回新对象，不修改原对象。",
    "final class、final byte[]、常量池复用、安全、线程安全、hashCode不变、返回新对象", 2,
    "StringBuilder和StringBuffer的区别是什么？底层怎么扩容的？", [1]))

Q.append(("Java的异常体系：Error、Exception、RuntimeException的区别和各自典型例子。",
    "Throwable为根类。Error:JVM级别严重错误程序无法处理——OOM、StackOverflowError、NoClassDefFoundError。Exception分两类:(a)Checked Exception——编译器强制try-catch或throws声明(IOException、SQLException)，代表可恢复的外部异常; (b)RuntimeException——非受检编译器不强制处理，通常是编程错误(NPE、IndexOutOfBoundsException、IllegalArgumentException)。最佳实践:不catch Error; Checked Exception要合理处理而非空catch; 避免用异常控制业务流程。",
    "Error、Checked Exception、RuntimeException、Throwable、NPE、OOM、空catch", 1,
    "try-catch-finally中finally一定会执行吗？什么情况下不会？", [1]))

# ---- JVM (tag 11) + Java (1) ----
Q.append(("JVM内存区域划分：哪些区域是线程私有的？哪些是线程共享的？",
    "线程私有:(1)程序计数器——当前线程执行的字节码行号; (2)虚拟机栈——每个方法创建栈帧(局部变量表/操作数栈/动态链接/返回值); (3)本地方法栈——Native方法服务。线程共享:(1)堆——对象实例和数组，GC主要区域，分新生代(Eden+S0+S1)和老年代; (2)方法区/MetaSpace(JDK8+)——类信息/常量/静态变量/JIT编译缓存，用本地内存。直接内存:NIO DirectByteBuffer使用，不在JVM堆内。",
    "程序计数器、虚拟机栈、本地方法栈、堆、MetaSpace、线程私有、线程共享、新生代、老年代、Eden S0 S1", 2,
    "JDK8为什么用MetaSpace替代永久代？MetaSpace会OOM吗？", [11,1]))

Q.append(("JVM类加载机制和双亲委派模型是什么？哪些场景会破坏双亲委派？",
    "类加载5阶段:加载→验证→准备→解析→初始化。类加载器层级:Bootstrap(rt.jar)→Extension(jre/lib/ext)→Application(classpath)。双亲委派:每层先委托父加载器加载，父找不到才自己加载——防止核心类被篡改(如自定义java.lang.String无法加载)。破坏场景:(1)JDBC——DriverManager由Bootstrap加载但驱动由AppClassLoader加载，需ThreadContextClassLoader; (2)Tomcat——每个WebApp独立ClassLoader隔离应用; (3)SPI——ServiceLoader默认用AppClassLoader打破。",
    "加载验证准备解析初始化、双亲委派、Bootstrap、Extension、Application、SPI、ThreadContextClassLoader、Tomcat隔离", 3,
    "Tomcat为什么要打破双亲委派？不同Web应用之间如何做到类隔离？", [11,1]))

Q.append(("JVM垃圾回收算法：标记-清除、标记-复制、标记-整理的各自优劣？",
    "标记-清除:标记存活→清除未标记，简单但有内存碎片。标记-复制:分两块内存，存活对象复制到另一块→清空当前块，无碎片但内存利用率仅50%，适合新生代(98%对象朝生夕死)。HotSpot Eden:S0:S1=8:1:1。标记-整理:存活对象移到一端→清理边界外，无碎片且利用率高，但移动对象需STW开销，适合老年代。实际组合:新生代用复制(Parallel Scavenge)，老年代用整理(Parallel Old); G1/ZGC用Region+并发标记+复制。",
    "标记清除碎片、标记复制Eden Survivor 8:1:1、标记整理移动对象STW、新生代老年代、G1 Region", 2,
    "G1收集器如何兼顾低延迟和高吞吐？Region设计解决了什么？", [11,1]))

Q.append(("什么情况会触发Full GC？如何进行JVM GC调优？",
    "触发Full GC:(1)老年代空间不足; (2)MetaSpace不足; (3)担保失败——老年代剩余<新生代对象总和; (4)CMS并发失败; (5)System.gc()。调优:(1)选收集器——低延迟用G1/ZGC，大堆用G1; (2)堆大小-Xms=-Xmx避免动态扩展; (3)调整新生代比例-XX:NewRatio和SurvivorRatio; (4)晋升阈值MaxTenuringThreshold; (5)用jstat/GC日志/Arthas/VisualVM分析。目标:减少Full GC次数、缩短STW时间。",
    "老年代不足、MetaSpace、担保失败、CMS并发失败、G1、ZGC、-Xms=-Xmx、GC日志、jstat、Arthas", 3,
    "你的项目中实际调过GC参数吗？怎么做GC日志分析的？", [11,1]))

# ---- Spring / Spring Boot (12,13) ----
Q.append(("Spring IoC容器和依赖注入(DI)的原理是什么？构造器注入和字段注入的优劣？",
    "IoC将对象创建和依赖管理交给Spring容器; DI是IoC的具体实现。容器:BeanFactory(基础)和ApplicationContext(高级:国际化/事件/AOP)。注入方式:(1)构造器注入——推荐，依赖不可变、易测试; (2)Setter注入——可选依赖; (3)字段注入——简洁但难测试(需反射)、隐藏依赖。容器启动:解析配置→BeanDefinition注册→BeanFactoryPostProcessor→实例化→属性填充→Aware回调→BeanPostProcessor前置→初始化→BeanPostProcessor后置→就绪。三级缓存解决循环依赖。",
    "IoC控制反转、DI依赖注入、BeanFactory、ApplicationContext、构造器注入推荐、BeanPostProcessor、三级缓存解决循环依赖", 2,
    "构造器注入vs字段注入，Spring官方推荐哪种？为什么？", [12,13]))

Q.append(("@Transactional声明式事务的原理、失效场景及解决方法？",
    "原理:通过AOP在方法前后由PlatformTransactionManager管理事务。传播行为:REQUIRED(默认)、REQUIRES_NEW、NESTED。失效场景:(1)同类内部调用绕过代理(this.method()); (2)方法非public; (3)异常被catch未抛出; (4)rollbackFor未包含实际异常类型(默认只回滚RuntimeException和Error); (5)数据库引擎不支持事务(如MyISAM); (6)多线程。解决:同类调用通过AopContext.currentProxy()获取代理; 指定rollbackFor=Exception.class; TransactionTemplate编程式事务。",
    "@Transactional、AOP、REQUIRED、REQUIRES_NEW、同类调用失效、非public失效、rollbackFor、TransactionTemplate", 2,
    "REQUIRED和REQUIRES_NEW分别适合什么场景？REQUIRES_NEW有什么风险？", [12,13,15]))

Q.append(("Spring Boot自动配置原理是什么？如何自定义一个Starter？",
    "流程:@SpringBootApplication→@EnableAutoConfiguration→@Import(AutoConfigurationImportSelector)→读取META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports→加载所有自动配置类→每个用@ConditionalOnClass/@ConditionalOnBean/@ConditionalOnProperty判断是否生效→满足则创建Bean。自定义Starter:(1)autoconfigure模块写@Configuration类+条件注解+@ConfigurationProperties; (2)starter模块空模块只引入autoconfigure和所需依赖; (3)在AutoConfiguration.imports中注册。",
    "@EnableAutoConfiguration、AutoConfigurationImportSelector、条件注解@ConditionalOnClass、@ConfigurationProperties、自定义Starter", 3,
    "@ConditionalOnMissingBean有什么坑？怎么排查自动配置不生效？", [13,12]))

Q.append(("Spring AOP的实现原理？JDK动态代理和CGLIB如何选择？",
    "AOP通过动态代理实现横切关注点。JDK代理:基于接口，InvocationHandler拦截。CGLIB:基于继承生成子类，MethodInterceptor拦截，不能代理final类/方法。核心概念:Aspect切面、JoinPoint连接点、Advice(@Before/@After/@Around/@AfterReturning/@AfterThrowing)、Pointcut切入点表达式。执行顺序:Around前→Before→目标方法→Around后→After→AfterReturning/AfterThrowing。注意:同类内部调用不触发AOP(this.method()绕过代理)。Spring Boot 2.x+默认CGLIB。",
    "动态代理、JDK代理接口、CGLIB子类、@Around环绕、内部调用绕过代理、final类限制、Aspect、Advice、Pointcut", 3,
    "同一个类中方法A调方法B，B上的@Transactional为什么不生效？怎么解决？", [12,13,1]))

# ---- MyBatis (15) + MySQL (20) ----
Q.append(("MyBatis中#{}和${}的区别是什么？为什么${}会导致SQL注入？",
    "#{}是预编译占位符→替换为?→PreparedStatement.setXxx()设置参数→防SQL注入+预编译提升性能。${}是字符串直接拼接进SQL→恶意输入可修改SQL语义(如传入 OR 1=1)→无法预编译。${}合法场景:动态表名/列名、ORDER BY/GROUP BY动态字段名——但必须做白名单校验，不允许用户输入直接拼接。",
    "#{}预编译PreparedStatement、?占位符、防SQL注入、${}字符串拼接、动态表名、白名单校验", 1,
    "如果必须用${}做动态排序，你怎么确保安全？写出白名单校验代码。", [15,26,1]))

Q.append(("MyBatis一级缓存和二级缓存有什么区别？使用注意事项？",
    "一级缓存(SqlSession级别):默认开启，同一SqlSession内相同查询只执行一次SQL。commit/close/clearCache时清空。二级缓存(Mapper/namespace级别):需显式配置<cache/>标签、实体类实现Serializable。不同SqlSession间共享但多表关联易脏数据。注意:不适合频繁更新数据; 分布式需Redis外部缓存替代。一级缓存作用范围小不易出问题; 二级缓存生产环境慎用(数据一致性风险)，通常推荐Redis替代。",
    "一级缓存SqlSession、二级缓存namespace、cache标签、Serializable、脏数据、Redis替代", 2,
    "生产环境你更倾向用MyBatis二级缓存还是Redis？为什么？", [15,22]))

# ---- MySQL (20) + SQL (26) + 数据结构(44) ----
Q.append(("MySQL InnoDB中B+Tree索引原理是什么？为什么不用B-Tree或二叉树？",
    "B+Tree:(1)所有数据存在叶子节点，非叶子只存索引key→一个节点存更多key→树更矮IO少; (2)叶子节点双向链表支持高效范围查询。vs B-Tree:非叶子也存数据→单个节点key少→树更高→IO多。vs二叉树:有序插入退化为链表O(n)。16KB页可存约1170个key，3层索引约2000万行仅3次IO。聚簇索引叶子存完整行; 二级索引叶子存主键值需回表; 覆盖索引避免回表。",
    "B+Tree、叶子存数据、非叶子存key、双向链表范围查询、3层2000万行3次IO、聚簇索引、二级索引回表、覆盖索引", 2,
    "什么是覆盖索引？如何利用覆盖索引避免回表？请举例说明。", [20,26,44]))

Q.append(("MySQL四种事务隔离级别是什么？InnoDB默认用什么？各解决了什么/未解决什么？",
    "READ UNCOMMITTED:允许读未提交，存在脏读/不可重复读/幻读。READ COMMITTED:只读已提交，解决脏读;存在不可重复读/幻读。REPEATABLE READ(InnoDB默认):同一事务内多次读取结果一致，解决脏读+不可重复读; 间隙锁部分解决幻读(非完全)。SERIALIZABLE:所有读加共享锁写加排他锁，串行执行解决全部问题但性能最差。MVCC通过Undo Log和ReadView实现非锁定一致性读，是隔离级别的底层支撑。",
    "读未提交、读已提交、可重复读RR、串行化、脏读、不可重复读、幻读、间隙锁、MVCC、ReadView、Undo Log", 3,
    "Oracle和PostgreSQL默认用RC，而MySQL默认用RR，设计哲学有什么不同？", [20,26]))

Q.append(("如何定位和优化一条慢SQL？EXPLAIN执行计划各字段的含义？",
    "定位:开启slow_query_log→mysqldumpslow分析; EXPLAIN; Performance Schema。EXPLAIN关键字段:type(const>eq_ref>ref>range>index>ALL)——ALL全表扫描最差; key——所用索引; rows——预估扫描行数; Extra——Using filesort/Using temporary性能杀手; Using index覆盖索引最佳。优化:(1)加联合索引遵循最左前缀; (2)覆盖索引避免回表; (3)SELECT指定字段不用*; (4)避免索引列上函数操作/隐式类型转换; (5)大表分库分表; (6)SQL重写用JOIN替代子查询。",
    "slow_query_log、EXPLAIN、type、key、rows、Using filesort、Using temporary、最左前缀、覆盖索引、避免函数操作", 2,
    "EXPLAIN中Using filesort怎么消除？什么情况下不可避免？", [20,26]))

Q.append(("MySQL主从复制原理是什么？主从延迟的原因及解决方案？",
    "原理:Master将数据变更写入binlog→Slave的I/O线程拉取binlog写入relay log→Slave的SQL线程回放。复制模式:异步(主写完返回，默认)、半同步(至少一个从确认收到binlog)、组复制(Paxos)。延迟原因:(1)从库机器差; (2)大事务回放慢; (3)从库负担重; (4)网络问题。解决:(1)并行复制(基于组提交的并行回放MySQL5.7+); (2)提升硬件; (3)关键业务强制读主库; (4)监控+告警。",
    "binlog、relay log、I/O线程、SQL线程、异步复制、半同步、并行复制、组复制、强制读主库", 3,
    "主从切换时如何保证数据一致性？MHA和Orchestrator各有什么优劣？", [20,53]))

# ---- Redis (22) + 分布式(53) ----
Q.append(("Redis五种基本数据类型及各自典型的应用场景？",
    "String:SDS，SET/GET/INCR。场景:缓存、计数器(INCR原子自增)、分布式锁(SETNX)。Hash:ziplist/hashtable。场景:对象存储可部分更新(用户信息)。List:quicklist，LPUSH/RPOP/BRPOP。场景:消息队列、最新N条记录。Set:hashtable，SADD/SINTER/SUNION。场景:标签、共同好友、抽奖去重。ZSet:skiplist+hashtable，ZADD/ZRANGEBYSCORE。场景:排行榜(按score)、延迟队列(score=执行时间戳)。其他:Bitmap(签到)、HyperLogLog(UV统计)、Geo(附近的人)、Stream(持久化MQ)。",
    "String、Hash、List、Set、ZSet、skiplist跳表、quicklist、排行榜、延迟队列、分布式锁、UV统计", 2,
    "ZSet底层为什么用跳表而不用红黑树？跳表有什么优势？", [22,44]))

Q.append(("Redis缓存穿透、缓存击穿、缓存雪崩的区别和各自的解决方案？",
    "缓存穿透:查询DB不存在的数据→缓存无→大量请求到DB。解决:布隆过滤器(预判一定不存在); 缓存空值(短过期); 参数校验。缓存击穿:热点key过期瞬间大量请求到DB。解决:互斥锁(SETNX串行化查DB); 逻辑过期(永不过期+异步刷新); 热点永不过期。缓存雪崩:大量key同时过期或Redis宕机。解决:过期时间加随机值(+/-30%打散); Redis高可用(主从+哨兵/集群); 多级缓存(Caffeine+Redis); 限流降级保护DB。",
    "缓存穿透、布隆过滤器、缓存空值、缓存击穿、互斥锁、逻辑过期、缓存雪崩、过期时间打散、多级缓存", 3,
    "布隆过滤器的原理是什么？为什么会有误判？误判率怎么计算？", [22,53]))

Q.append(("Redis持久化RDB和AOF的区别？如何选择与配置？",
    "RDB(快照):定期将内存数据保存为dump.rdb。BGSAVE fork子进程后台写。优点:文件紧凑恢复快、适合备份。缺点:两次快照间可能丢数据。AOF(追加):每条写命令追加到文件。fsync策略:always(安全慢)/everysec(折中推荐)/no。优点:最多丢1秒数据、可读。缺点:文件比RDB大、恢复慢。推荐:同时开启(RDB备份+AOF安全，重启优先加载AOF)。混合持久化(Redis4.0+):AOF重写时头部嵌入RDB二进制，兼顾恢复速度和数据安全。",
    "RDB快照、BGSAVE fork、AOF追加、always/everysec、AOF重写、混合持久化", 2,
    "AOF重写过程中新写入的数据怎么处理？会丢失吗？", [22]))

Q.append(("如何用Redis实现分布式锁？Redisson看门狗解决了什么问题？",
    "基础:SET key value NX EX timeout——原子设锁+过期防死锁。value=UUID+线程ID; Lua脚本原子校验value后删除(防释放别人的锁)。Redisson看门狗:每10秒自动续期30秒——解决锁过期任务未完成。可重入:Hash结构(hset key threadId 重入次数)。RedLock:向N个独立节点依次获取锁>N/2+1成功且总耗时<锁有效期(有争议，多数场景单节点即可)。锁必须配合幂等业务逻辑。",
    "SET NX EX、UUID防误删、Lua原子释放、看门狗自动续期、可重入Hash、RedLock N/2+1", 3,
    "RedLock的争议在哪里？为什么一般场景不需要RedLock？", [22,53]))

# ---- 计算机网络(47) + HTTP(49) + 操作系统(48) ----
Q.append(("TCP三次握手和四次挥手的过程？为什么握手是三次、挥手是四次？",
    "三次握手:(1)Client→Server SYN=1,seq=x; (2)Server→Client SYN+ACK,seq=y,ack=x+1; (3)Client→Server ACK,seq=x+1,ack=y+1。为什么三次:防止历史失效连接请求——旧SYN后到服务端回SYN+ACK若只两次则服务端单方面建连浪费资源。四次挥手:(1)Client→Server FIN; (2)Server→Client ACK(半关闭); (3)Server→Client FIN(数据发完); (4)Client→Server ACK→TIME_WAIT等2MSL。为什么四次:TCP全双工，双方都可发数据，ACK和FIN分开发。TIME_WAIT:确保最后ACK到达、让旧连接残留报文消失。",
    "SYN、ACK、FIN、三次握手防历史连接、四次挥手全双工、TIME_WAIT 2MSL、半关闭", 2,
    "TIME_WAIT过多会导致什么？tcp_tw_reuse安全吗？", [47,48]))

Q.append(("HTTPS的加密原理是什么？SSL/TLS握手流程是怎样的？",
    "HTTPS=HTTP+SSL/TLS。TLS1.2握手:(1)ClientHello加密套件+随机数; (2)ServerHello选定套件+随机数+证书(含公钥); (3)Client验证证书链→生成PreMaster Secret→用Server公钥加密发送; (4)双方各自派生对称密钥(会话密钥); (5)Finished→后续对称密钥通信。TLS1.3改进:握手1-RTT(ECDHE+证书一起发); 去除RSA只保留前向安全的ECDHE; 0-RTT恢复。原理:非对称加密交换密钥+对称加密传输数据+数字证书防篡改。",
    "非对称交换密钥、对称传输数据、证书链、PreMaster Secret、ECDHE前向安全、TLS1.3 1-RTT 0-RTT", 3,
    "什么是中间人攻击？HTTPS如何防止中间人篡改？", [49,47]))

Q.append(("HTTP/1.1、HTTP/2、HTTP/3的主要区别和各自改进？",
    "HTTP/1.1:持久连接、管道化(队头阻塞)、Host头。HTTP/2:(1)二进制分帧; (2)多路复用同TCP并发多请求; (3)头部压缩HPACK; (4)服务器推送; (5)流优先级。但TCP层面仍有队头阻塞。HTTP/3:基于QUIC(UDP)→彻底解决TCP队头阻塞、0-RTT建连更快、连接迁移切换网络不断连、内置TLS1.3。缺点:UDP可能被QoS限制; CPU开销比TCP高。目前主流浏览器都支持HTTP/3。",
    "HTTP/1.1持久连接、HTTP/2多路复用二进制帧HPACK头部压缩、HTTP/3 QUIC 0-RTT连接迁移、队头阻塞", 3,
    "HTTP/2已多路复用了，为什么还需要HTTP/3的QUIC？", [49,47]))

# ---- 数据结构(44) + 算法(45) + 设计模式(46) ----
Q.append(("常用排序算法的时间/空间复杂度及稳定性？Java中如何选择排序算法？",
    "快速排序:O(nlogn)平均O(n²)最坏、不稳定、原地。归并排序:O(nlogn)、稳定、O(n)空间。堆排序:O(nlogn)、不稳定、原地。Java:Arrays.sort(基本类型)用双轴快排(不需要稳定性); Arrays.sort(对象)用TimSort(归并+插入混合，稳定)。TopK用小顶堆O(nlogK); 海量数据外部排序用归并。稳定性重要性:对象排序中先按A字段再按B字段——稳定排序才能保留第一次排序的相对顺序。",
    "快速排序、TimSort、归并、堆排序、稳定性、O(nlogn)、双轴快排、二分插入、小顶堆TopK", 2,
    "Java中为什么基本类型用快排而对象用TimSort？稳定性为什么对对象重要？", [45,1,44]))

Q.append(("HashMap的底层数据结构和put/get流程？JDK1.8做了哪些优化？",
    "底层:数组(Node[])+链表+红黑树。put:(1)计算hash=key.hashCode()^高16位扰动; (2)(n-1)&hash得下标; (3)空则直接插入; 不空→(4)key相同覆盖; (5)链表遍历(>=8转红黑树); (6)size>threshold扩容翻倍; (7)扩容时拆分链表(判断e.hash&oldCap)。JDK8优化:(1)链表→红黑树O(logn); (2)头插→尾插(避免并发resize死循环); (3)hash函数简化高16位异或低16位。",
    "数组+链表+红黑树、扰动函数、扩容翻倍、尾插避死循环、树化阈值8、负载因子0.75", 2,
    "为什么树化阈值是8而不是更小？退化阈值为什么是6？", [1,44]))

Q.append(("单例模式的几种实现方式？为什么推荐枚举单例？",
    "饿汉式:类加载时创建，线程安全但非懒加载。双重检查锁(DCL):volatile防指令重排+两次null判断+synchronized。静态内部类(LazyHolder):利用类加载机制延迟初始化+线程安全。枚举单例:enum Singleton{INSTANCE;}，由JVM保证线程安全+防反射攻击+防反序列化创建新实例，最简洁安全。DCL的volatile必要性:new Object()三步(分配内存→初始化→引用指向)可能被重排，第二个null判断可能拿到未初始化完成的对象。",
    "饿汉式、DCL双重检查锁、volatile防指令重排、LazyHolder类加载、枚举单例防反射防序列化", 2,
    "DCL单例中volatile的作用是什么？去掉会有什么问题？结合指令重排解释。", [46,1,19]))

Q.append(("SOLID五大设计原则是什么？在Java开发中如何体现？",
    "S(单一职责):一个类只负责一件事——UserService只管业务，UserRepository只管数据。O(开闭原则):对扩展开放对修改关闭——定义接口+多实现(如ResumeAnalyzer接口+RuleBased/AI实现)。L(里氏替换):子类可完全替换父类——子类不改变父类方法契约。I(接口隔离):接口小而专——不强迫实现者依赖不需要的方法。D(依赖倒置):依赖抽象而非具体——Service依赖接口通过DI注入，换实现不改调用方。Spring IoC/AOP本身就是SOLID的典范。",
    "单一职责、开闭原则、里氏替换、接口隔离、依赖倒置、Spring IoC/AOP、面向接口编程", 2,
    "你最近写的代码中有没有违反SOLID的？怎么重构的？", [46,12]))

# ---- 操作系统(48) + Linux(34) ----
Q.append(("进程和线程的区别是什么？协程又是什么？各自适用什么场景？",
    "进程:OS资源分配基本单位，独立地址空间，IPC通信，上下文切换开销大(需切换页表)。线程:CPU调度基本单位，同进程共享堆/全局变量，栈私有，切换开销小，需同步机制。协程:用户态调度无需内核参与，切换只保存寄存器(比线程更快)，单线程内协作式调度无锁问题，内存开销极小(KB级)。Go goroutine、Kotlin协程、Python asyncio都是协程。适用:进程=应用隔离; 线程=CPU密集型并行; 协程=IO密集型高并发百万级连接。",
    "进程独立地址空间、线程共享堆、协程用户态调度、无锁、goroutine、IO密集型高并发", 2,
    "Go的goroutine和Java的Virtual Thread(Project Loom)有什么区别？", [48,1,7]))

Q.append(("死锁的四个必要条件是什么？如何预防和避免死锁？",
    "四个必要条件(缺一不可):(1)互斥——资源每次只能一个进程用; (2)持有并等待——进程持资源同时等待其他资源; (3)不可剥夺——已分配资源不可强行抢走; (4)环路等待——进程间形成资源等待环路。预防(破坏任一条件):(1)资源虚拟化(SPOOLing); (2)一次性申请所有资源; (3)资源可抢占; (4)资源有序分配(按编号顺序)。避免:银行家算法预判安全性。Java实践:(1)按固定顺序获取锁; (2)tryLock(timeout)超时放弃; (3)ThreadMXBean检测死锁。",
    "互斥、持有并等待、不可剥夺、环路等待、资源有序分配、银行家算法、tryLock超时、ThreadMXBean检测", 2,
    "Java中如何定位和排查线上死锁？用jstack怎么看？", [48,1,19]))

# ---- 前端 Vue/React/JS (37,38,5,6,36,41) ----
Q.append(("Vue 3的响应式原理是什么？Proxy相比Vue 2的defineProperty有什么优势？",
    "Vue 3用Proxy代理整个对象。getter中track()收集依赖(哪个effect用了哪个属性)，setter中trigger()触发更新。优势:(1)能检测数组索引修改和length变化(defineProperty需重写数组方法); (2)能检测属性新增/删除(defineProperty需Vue.set/delete); (3)懒代理——只有访问到的嵌套对象才被代理; (4)Proxy直接代理对象无需遍历所有属性初始化。ref用getter/setter实现基本类型响应式。组合式API(setup)让逻辑关注点聚合。副作用(effect)用栈记录当前活跃effect实现自动依赖收集。",
    "Proxy代理、track依赖收集、trigger更新、defineProperty数组限制、Vue.set、懒代理、ref .value、effect栈", 3,
    "Vue 3的ref和reactive有什么区别？什么时候用哪个？", [37,5]))

Q.append(("React Hooks的原理和使用规则？useEffect的依赖数组怎么用？",
    "Hooks让函数组件拥有状态和副作用。原理:组件实例维护hooks链表(fiber.memoizedState)，每次渲染按调用顺序取对应hook。规则:(1)只在最顶层调用不在条件/循环中——保持顺序一致; (2)只在React函数组件或自定义Hook中调用。useState返回[state,dispatch]; useEffect渲染后异步执行副作用，返回cleanup函数在下一次effect前或卸载时调用。依赖数组:[]=仅mount执行; 无依赖=每次渲染执行; [a,b]=a或b变化执行。useMemo/useCallback避免不必要重计算和子组件重渲染。",
    "hooks链表、调用顺序、fiber.memoizedState、useEffect cleanup、依赖数组[]、useMemo、useCallback、React.memo", 3,
    "useEffect中的cleanup函数什么时候执行？return的时机？", [38,5]))

Q.append(("CSS Flex和Grid布局的区别？各自适合什么场景？",
    "Flexbox:一维布局——沿主轴(row或column)排列，适合组件级(导航栏、卡片列表、居中)。核心属性:display:flex, justify-content主轴对齐, align-items交叉轴对齐, flex-grow/shrink/basis。Grid:二维布局——行列同时控制，适合页面级(整体结构、仪表盘、画廊)。核心属性:display:grid, grid-template-columns/rows定义行列轨道, gap间距, grid-template-areas命名区域。可组合:页面大结构用Grid，组件内部排列用Flex。两者都比float/定位更语义化。",
    "Flex一维、主轴交叉轴、justify-content、align-items、Grid二维、grid-template-columns、命名区域", 1,
    "什么场景你会选择Grid而不是Flex？", [36,35]))

Q.append(("Vite为什么比Webpack快？ESBuild和Rollup在Vite中分别做什么？",
    "开发模式ESBuild预构建依赖(Go语言比JS快10-100倍)。生产用Rollup(成熟tree-shaking和代码分割)。HMR基于ESM按需热更新——只失效修改模块的依赖链，不论项目多大都很快(Webpack需重新打包整个chunk)。冷启动:不打包源码，按浏览器请求按需编译(利用ESM import)，首次只编译需要的页面。预构建:将CommonJS/UMD转ESM; 合并多模块减少HTTP请求。Rollup优势:天然ESM、tree-shaking更彻底。",
    "ESBuild Go语言、ESM按需编译、HMR依赖链失效、预构建转ESM、Rollup tree-shaking、冷启动不打包", 2,
    "什么情况下Vite开发和生产构建的行为不一致？怎么排查？", [41,40]))

# ---- 中间件 Kafka/RabbitMQ/RocketMQ (27,28,29) + Docker/K8s (31,32) ----
Q.append(("Kafka为什么高吞吐？它的分区和消费者组机制是怎样的？",
    "高吞吐原因:(1)顺序写磁盘(append-only log)比随机读写快; (2)零拷贝sendfile从Page Cache直发网卡不经过用户态; (3)批量压缩减少网络IO; (4)分区并行读写。分区:每个topic多partition，partition内有序跨分区无序。消费者组:同组消费者各自负责不同分区(一区只能被同组一个消费者消费)——实现负载均衡和水平扩展; 不同组独立消费。ISR:与Leader同步的副本集合。ACK:0/1/all。",
    "顺序写磁盘、零拷贝sendfile、批量压缩、partition分区有序、消费者组负载均衡、ISR、ACK all", 3,
    "Kafka的exactly-once语义怎么实现？幂等+事务机制是什么？", [27,53]))

Q.append(("RabbitMQ的交换机(Exchange)类型有哪些？死信队列怎么用？",
    "Exchange类型:(1)Direct——routing key完全匹配; (2)Fanout——广播所有绑定队列; (3)Topic——routing key通配符(*一个词/#零或多词); (4)Headers——按消息Header匹配。死信队列(DLQ):消息变死信时自动转发。死信条件:(1)消息被拒绝(requeue=false); (2)TTL过期; (3)队列满。应用:延迟队列(TTL+DLQ)、异常消息留存分析、重试队列。可靠性:publisher confirm、consumer ack(手动)、持久化、镜像队列。",
    "Direct、Fanout、Topic通配符、死信队列DLQ、TTL过期、延迟队列、publisher confirm、consumer ack", 2,
    "如何用RabbitMQ实现延迟队列？有哪几种实现方式？各有什么优缺点？", [28,53]))

Q.append(("Docker镜像的分层结构是什么？多阶段构建有什么优势？",
    "分层:每个Dockerfile指令(RUN/COPY/ADD)生成一层只读layer，镜像=多层stack。容器运行时加可写层。好处:相同基础层多镜像共享节省空间和拉取时间。写时复制:容器修改文件时从下层Copy到可写层再改。多阶段构建:构建阶段(编译安装)和生产阶段(仅复制产物)分离——最终镜像不含编译工具和中间产物，体积大幅减小。优化:RUN合并减少层数; .dockerignore排除无关文件; 变化频率低的层放前面利用缓存。",
    "只读layer分层、可写层、写时复制、多阶段构建减小镜像、RUN合并、.dockerignore、缓存优化", 2,
    "Docker COPY和ADD指令有什么区别？什么时候用ADD？", [31]))

Q.append(("Kubernetes Pod、Deployment、Service分别是什么？它们的协作关系？",
    "Pod:最小调度单元，含一个或多个容器共享网络和存储卷。Deployment:管理Pod声明式控制器——指定期望副本数/Pod模板/更新策略(RollingUpdate/Recreate)→自动维持实际状态=期望。Service:为Pod提供稳定入口(ClusterIP/NodePort/LoadBalancer)，通过label selector匹配Pod，kube-proxy实现负载均衡。协作:Deployment创建Pod→Service暴露Pod→外部访问。ConfigMap/Secret管理配置; Ingress HTTP路由; HPA自动扩缩; 健康检查Liveness/Readiness/Startup。",
    "Pod最小调度单元、Deployment声明式副本、RollingUpdate滚动更新、Service稳定入口、ClusterIP/NodePort/LoadBalancer、HPA", 3,
    "Deployment的RollingUpdate过程中流量是怎么平滑切换的？", [32,31]))

# ---- 工程实践 (50-57) ----
Q.append(("Git的rebase和merge有什么区别？什么时候用rebase？",
    "merge:保留完整历史产生新merge commit，非线性但完整。rebase:将当前分支提交重放到目标分支顶端→线性历史无多余merge commit。rebase优势:历史整洁、git log易跟踪。黄金法则:不对已推送的公共分支rebase(改变SHA导致协作冲突)。建议:本地分支rebase到主分支再merge; PR合入用Squash and Merge保持主分支干净; cherry-pick提取单提交。rebase冲突:逐个commit解决→git rebase --continue/--skip/--abort。",
    "merge产生合并提交、rebase线性历史重写SHA、不对公共分支rebase、Squash and Merge、cherry-pick", 2,
    "rebase时遇到冲突怎么处理？--continue/--skip/--abort的适用场景？", [50]))

Q.append(("CI/CD流水线一般包含哪些阶段？蓝绿部署和金丝雀发布有什么区别？",
    "CI:push→触发→编译+单测→代码扫描(SonarQube)→构建镜像→推镜像仓库。CD:拉镜像→部署测试环境→自动化测试→审批→预发布→生产。部署策略:(1)蓝绿:两套完整环境，流量一键切换，回滚快(切回旧环境)——成本高需双倍资源; (2)金丝雀:逐渐放量(5%→20%→100%)观察指标，异常自动回滚——风险最低; (3)滚动更新:K8s逐个替换Pod。选型:核心业务用金丝雀，小项目用蓝绿或滚动。",
    "CI自动构建测试、CD自动部署、Blue-Green蓝绿、Canary金丝雀逐渐放量、RollingUpdate滚动、GitHub Actions", 2,
    "蓝绿部署和金丝雀发布的核心区别？什么场景分别选哪种？", [51,31,32]))

Q.append(("微服务架构的优缺点？如何合理地拆分微服务？",
    "优点:独立部署、技术异构、独立扩缩、团队自治。缺点:分布式复杂性(网络延迟、事务一致性); 运维成本高(监控/日志/链路追踪/CI/CD); 数据一致性(分布式事务比单体复杂); 调试困难。拆分原则:(1)DDD限界上下文——按业务领域拆分; (2)每个服务独立数据库(去中心化); (3)API/消息通信。不拆分过早——先单体验证业务再逐步拆; 拆分不过细——一个服务做一件事且只做一件事。何时拆:团队变大/模块耦合低/独立部署需求出现。",
    "独立部署、技术异构、独立扩缩、分布式复杂性、DDD限界上下文、独立数据库、不过早拆分", 3,
    "一个单体应用什么时候应该开始拆分微服务？判断标准是什么？", [52,53,57]))

Q.append(("分布式系统中CAP理论的含义？BASE理论如何指导实践？",
    "CAP:(1)Consistency一致性——所有节点同一时间看到相同数据; (2)Availability可用性——每个请求获得非错误响应; (3)Partition Tolerance分区容忍——网络分区时系统仍工作。任何分布式系统最多满足两个——因P必须保证(网络故障不可避免)所以必须在C和A之间取舍。CP:放弃A保强一致性(ZK/Etcd→选举期间暂不可用)。AP:放弃C保最终一致性(Eureka/Cassandra)。BASE对CAP补充:(1)Basically Available基本可用——允许降级; (2)Soft State软状态——允许中间态; (3)Eventually Consistent最终一致性。",
    "一致性、可用性、分区容忍、CP(ZK Etcd)牺牲可用性、AP(Eureka)最终一致、BASE基本可用、软状态、最终一致性", 3,
    "你们的项目在CAP中怎么取舍？哪些场景容忍暂时不一致？", [53,52]))

Q.append(("RESTful API设计最佳实践？如何做版本管理？",
    "资源命名:名词复数(/users, /orders)，层级关系(/users/{id}/orders)。HTTP方法:GET查询(安全幂等)、POST创建(非幂等)、PUT全量更新(幂等)、PATCH部分更新、DELETE删除(幂等)。状态码:200成功、201创建、204无内容、400参数错、401未认证、403无权限、404不存在、409冲突、500服务错。分页:?page=1&size=20或?cursor=xxx游标分页。版本管理:(1)URL /api/v1/users; (2)Header Accept:application/vnd.api.v2+json; (3)参数?version=2。过滤排序:?filter=status:active&sort=-created_at。Swagger/OpenAPI自动生成文档。",
    "名词复数、GET/POST/PUT/DELETE、幂等性、状态码200/201/400/401/403/404/500、分页、版本管理、Swagger", 2,
    "POST和PUT的核心区别？什么时候用PATCH？", [56,49]))

Q.append(("软件测试金字塔各层的作用？TDD的red-green-refactor循环是什么？",
    "金字塔:底层单元测试(占比最大、快、成本低)→中间集成/API测试→顶层E2E/UI测试(占比最少、最慢最脆弱)。单元测试:测单个函数方法，Mock外部依赖，<100ms快速反馈。集成测试:测组件协作(Controller→Service→DB)。E2E:模拟用户操作完整流程。TDD:Red(写失败测试)→Green(写最少代码让测试通过)→Refactor(重构代码不改变行为)。高覆盖率自然达成、设计更解耦。Mock vs Stub:Mock验证行为、Stub预设数据。不追求100%覆盖率，80%+关键路径即可。",
    "测试金字塔、单元测试、集成测试、E2E、TDD Red-Green-Refactor、Mock验证行为、Stub预设数据、80%覆盖率", 2,
    "什么情况下你会选择跳过写单元测试？哪些代码是必须测的？", [54,57]))

Q.append(("系统设计：如何设计一个秒杀系统？需要考虑哪些方面？",
    "核心挑战:超高并发、防超卖、防刷单。架构:(1)前端:静态化+CDN、按钮防重复(置灰+倒计时)、答题/验证码防脚本; (2)网关层:限流(Sentinel令牌桶)、黑名单; (3)服务层:Redis预减库存(DECR原子操作)、内存标记售罄直接返回、异步下单(MQ削峰); (4)DB层:乐观锁(WHERE version=旧值)防超卖。降级:限流→排队→逐步放行。数据一致性:Redis减库存失败回滚、MQ可靠消费(ACK+重试)。压测:JMeter找瓶颈。监控:实时大盘。",
    "CDN静态化、验证码防脚本、令牌桶限流、Redis预减库存DECR原子、MQ削峰异步下单、乐观锁防超卖、JMeter压测", 3,
    "Redis预减库存后下单失败怎么回滚？事务一致性怎么保证？", [55,22,53]))


# ---- 补充其他标签题目 ----
# Python(4), C(2), C++(3), Go(7), Rust(8), Kotlin(9), PHP(10)
Q.append(("Python中列表(list)和元组(tuple)的区别？什么场景用哪种？",
    "list可变(可增删改)，用方括号[]; tuple不可变(创建后不能改)，用圆括号()。list方法多(append/extend/remove/pop/sort); tuple方法少(count/index)。tuple可作为dict的key(不可变hashable)，list不行。tuple比list内存占用小(无需over-allocation)。场景:list用于动态数据集(用户列表、待处理队列); tuple用于固定数据(坐标、配置、函数多返回值)、dict key。",
    "list可变、tuple不可变、hashable可作key、内存占用、多返回值", 1,
    "tuple真的完全不可变吗？如果tuple里包含一个list呢？", [4]))

Q.append(("C语言中指针和数组的关系是什么？野指针如何产生和避免？",
    "数组名在表达式中退化为指向首元素的指针(除sizeof和&外)。a[i]等价于*(a+i)。野指针:指向已释放或未知内存的指针。产生原因:(1)未初始化; (2)free后未置NULL; (3)返回局部变量地址。避免:(1)初始化指针为NULL; (2)free后立即置NULL; (3)不返回栈变量地址; (4)用valgrind/ASan检测; (5)代码规范:谁分配谁释放。",
    "数组退化指针、sizeof差异、野指针free未置NULL、valgrind、ASan、栈变量地址", 2,
    "malloc和calloc的区别？realloc有什么坑？", [2,48]))

Q.append(("C++智能指针unique_ptr、shared_ptr、weak_ptr的区别和使用场景？",
    "unique_ptr:独占所有权，不可拷贝只可移动(move)，离开作用域自动delete，零开销。场景:工厂返回值、容器元素、PIMPL惯用法。shared_ptr:共享所有权，引用计数(原子操作)，计数归零delete。控制块存引用计数。场景:多对象共享资源(但注意循环引用)。weak_ptr:不增加引用计数，观察shared_ptr对象，lock()获取shared_ptr(已释放则空)。场景:打破循环引用、缓存、观察者模式。make_shared单次分配对象+控制块(效率更高)。RAII+智能指针实现自动资源管理。",
    "unique_ptr独占move、shared_ptr引用计数、weak_ptr打破循环、控制块、make_shared、RAII", 2,
    "shared_ptr的循环引用怎么造成内存泄漏？weak_ptr怎么打破？请画图或写代码说明。", [3,8]))

Q.append(("TypeScript中interface和type的区别？什么时候用哪个？",
    "相同点:都可描述对象形状、函数签名。不同点:(1)interface可被extends和implements扩展，type用交叉类型&扩展; (2)interface同名自动合并(declaration merging)，type同名报错; (3)type可表示联合类型|、交叉类型&、元组、字面量类型，interface不行; (4)interface更面向对象，type更函数式。推荐:描述对象/类的形状优先用interface(可扩展+合并); 需要联合类型/映射类型/工具类型用type。大多数场景两者可互换，团队统一规范即可。",
    "interface、type、extends扩展、declaration merging、联合类型|、交叉类型&、元组、字面量类型", 2,
    "TypeScript的unknown和any有什么区别？什么时候用unknown？", [6,5]))

Q.append(("Go的goroutine和channel如何实现并发？什么是CSP并发模型？",
    "goroutine:Go运行时管理的轻量级用户态线程(初始2KB栈可动态扩缩)，创建只需go func()。CSP(通信顺序进程):goroutine之间不共享内存而通过channel通信——Don't communicate by sharing memory; share memory by communicating。channel:无缓冲(同步阻塞)vs有缓冲(缓冲满前异步)。select监听多channel实现超时/非阻塞/多路复用。GMP调度:G(goroutine)、M(OS线程)、P(逻辑处理器=GOMAXPROCS)，P持有本地G队列，工作窃取。百万级goroutine并发轻松实现。",
    "goroutine轻量级、channel通信、CSP模型、select多路、GMP、GOMAXPROCS、工作窃取、共享内存vs通信", 3,
    "go func()和Java new Thread()在内存和调度开销上差多少？", [7,48]))

Q.append(("Kotlin协程的原理？和Java线程、Go goroutine有什么不同？",
    "Kotlin协程:在JVM上实现的用户态轻量级并发。suspend函数标记挂起点，编译时转为CPS(Continuation Passing Style)状态机。协程可挂起而不阻塞线程——IO操作时释放线程给其他协程使用。CoroutineScope管理生命周期，结构化并发(父协程等子协程完成)。调度器:Dispatchers.Main/IO/Default。vs Java线程:协程是轻量级(不映射1:1到OS线程); vs Go goroutine:都是用户态协作，但Kotlin协程在JVM上受限于JVM线程模型。适合:Android异步、后端高并发IO。",
    "suspend挂起点、CPS状态机、协程不阻塞线程、结构化并发、CoroutineScope、Dispatchers", 3,
    "Kotlin协程的launch和async有什么区别？什么时候用哪个？", [9,1]))

Q.append(("Spring Cloud微服务治理的核心组件有哪些？各自解决什么问题？",
    "Nacos/Eureka:服务注册发现(服务上线注册→下线剔除→负载均衡获取实例列表)。Gateway/Zuul:API网关(统一入口、路由转发、鉴权、限流)。OpenFeign:声明式HTTP客户端(接口+注解调用远程服务，集成Ribbon负载均衡)。Sentinel/Hystrix:熔断降级(异常/慢调用比例超阈值→熔断→半开试探→恢复)。Config(Nacos/Apollo):配置中心(热更新、灰度)。Sleuth+Zipkin:链路追踪(跨服务traceId定位瓶颈)。CAP取舍:Eureka AP(优先可用性)，Nacos支持CP/AP切换。",
    "Nacos注册发现、Gateway网关、OpenFeign声明式调用、Sentinel熔断降级、配置中心、链路追踪、CAP取舍", 3,
    "Sentinel和Hystrix的熔断策略有什么不同？滑动窗口怎么算的？", [14,52]))

Q.append(("PostgreSQL相比MySQL有哪些独特优势？窗口函数怎么用？",
    "PG优势:(1)更全面SQL标准支持(CTE、窗口函数、LATERAL JOIN); (2)JSONB原生JSON存储支持索引和查询(GIN索引); (3)全文搜索内置(tsvector/tsquery); (4)丰富扩展(PostGIS地理信息、TimescaleDB时序); (5)多版本并发MVCC无需回滚段更干净; (6)DDL可回滚(事务性DDL)。窗口函数:ROW_NUMBER()/RANK()/DENSE_RANK()/LAG()/LEAD()/SUM()OVER(PARTITION BY ... ORDER BY ...)。典型场景:分组TopN、环比同比计算、移动平均。PG更适合复杂查询和数据分析场景。",
    "SQL标准、JSONB GIN索引、CTE、窗口函数、DDL可回滚、PostGIS、TimescaleDB", 2,
    "MySQL和PostgreSQL在MVCC实现上有什么不同？各有什么优劣？", [21,26]))

Q.append(("MongoDB的适用场景？和MySQL相比有什么优势和劣势？",
    "适用场景:(1)灵活Schema——文档模型适合字段不固定、嵌套结构的数据(日志/爬虫结果); (2)高并发读写——副本集读写分离; (3)快速原型——无需预定义表结构。优势:JSON/BSON存储与前端天然亲和; 水平扩展分片集群; 聚合管道比SQL更链式可读。劣势:无JOIN(需embedding或$lookup，性能不如关系型); 事务支持较晚(4.0+多文档事务但性能不如MySQL); 数据分析不如关系型成熟。不是MySQL替代品，是互补——MySQL适合结构化交易数据，MongoDB适合半结构化和快速迭代。",
    "文档模型、灵活Schema、BSON、聚合管道、副本集、分片集群、无JOIN、事务较晚", 2,
    "MongoDB的$lookup和MySQL的JOIN有什么区别？什么场景用embedding代替？", [23,20]))

Q.append(("Elasticsearch的倒排索引原理？为什么ES比MySQL更适合全文搜索？",
    "倒排索引:对文档分词→建立词条(Term)→文档ID列表的映射。查询时直接根据词条查文档列表O(1)，无需全表扫描。ES在Lucene基础上做分布式:索引分片水平扩展; 近实时刷新(1s默认); 相关性评分(TF-IDF/BM25)排序结果。vs MySQL LIKE:%keyword%全表扫描极慢; 全文索引(ngram/FULLTEXT)可用但分词/相关度排序不如ES。ES适用:搜索引擎、日志分析(ELK)、商品搜索推荐。注意:ES不是数据库，不保证ACID事务，应作为二级索引从MySQL同步数据。",
    "倒排索引、分词Term、TF-IDF、BM25评分、索引分片、近实时刷新、ELK日志分析、二级索引", 2,
    "ES写入的数据为什么近实时(1s)才可搜索？refresh间隔怎么调？", [24,20]))

Q.append(("Nginx作为反向代理和负载均衡的工作原理？常用配置有哪些？",
    "反向代理:客户端→Nginx→后端服务器(隐藏后端IP、统一入口SSL终结)。负载均衡策略:轮询(默认)、加权轮询(weight)、ip_hash(Session保持)、least_conn(最少连接)、fair(响应时间)。常用配置:upstream定义后端集群; location匹配URL规则; proxy_pass转发; proxy_set_header透传请求头。其他:动静分离(location ~ .*\.(js|css)$); gzip压缩; 限流limit_req_zone; HTTPS配置ssl_certificate; 缓存proxy_cache。Nginx事件驱动(epoll)单机数万并发连接。",
    "反向代理、负载均衡、轮询ip_hash、upstream、proxy_pass、动静分离、限流、HTTPS、epoll事件驱动", 2,
    "Nginx的ip_hash和least_conn分别在什么场景下使用？有什么局限性？", [30,34]))

Q.append(("Docker Compose中如何编排多容器应用？network和volume怎么配置？",
    "Compose用YAML定义多容器服务(services)、网络(networks)、数据卷(volumes)。docker-compose up一键启动全栈。关键配置:build/Dockerfile构建; image指定镜像; ports端口映射; environment/env_file环境变量; depends_on启动依赖(但不等待服务就绪，需healthcheck+condition)。network:默认创建bridge网络容器间可用服务名互相访问; 可自定义网络隔离。volume:命名卷(docker volume管理)/绑定挂载(bind mount开发热更新)。tip:用depends_on+healthcheck确保启动顺序; 生产环境不要depends_on(应靠应用层容错)。",
    "docker-compose.yml、services、ports映射、depends_on、healthcheck、network服务名互访、volume绑定挂载", 2,
    "depends_on只等容器启动了不等服务就绪，怎么解决MySQL没就绪就启动应用的问题？", [31,32]))

Q.append(("Element Plus表单校验怎么用？自定义校验规则怎么实现？",
    "el-form绑定model和rules，el-form-item指定prop。rules定义每个字段的验证规则:required必填、type类型、min/max长度、pattern正则、validator自定义函数。自定义校验:validator(rule, value, callback)——callback()成功、callback(new Error('msg'))失败。异步校验:callback在async/await后调用。表单提交:el-form.validate(valid=>{if(valid){...}})。resetFields重置。常见场景:密码一致性校验(validator中比较两个字段)、唯一性校验(async validator调API)。Element Plus表单校验基于async-validator库。",
    "el-form model rules、prop、required、validator自定义、callback、异步校验async-validator", 1,
    "Element Plus动态增减表单项(动态表单)怎么实现校验？", [42,37]))

Q.append(("ECharts如何实现折线图、柱状图、饼图的组合？图表自适应怎么做？",
    "配置option:series数组定义各系列(type:'line'/'bar'/'pie')。grid控制绘图区域。legend图例联动。tooltip提示框(formatter自定义格式)。自适应:(1)监听window resize→chart.resize(); (2)init用容器100%宽高; (3)debounce防抖resize事件。性能:(1)大数据量用sampling采样或large模式; (2)动画过多用animation:false; (3)按需引入模块(import {BarChart} from echarts/charts)。交互:click事件(seriesIndex/dataIndex定位数据)、dispatchAction(高亮/tooltip/showTip编程式触发)。主题:echarts.init(dom, 'dark')或自定义主题JSON。",
    "series、grid、legend、tooltip、resize自适应、debounce防抖、sampling采样、dispatchAction编程触发", 2,
    "ECharts大数据量(10万+点)怎么优化？sampling和large模式有什么区别？", [43,37]))

Q.append(("Git分支管理最佳实践？Git Flow和GitHub Flow有什么区别？",
    "Git Flow:main(生产)+develop(开发)+feature(功能)+release(发布)+hotfix(修复)。适合有固定发布周期的传统项目。较复杂分支多。GitHub Flow:main(可部署)+feature分支→PR合入main→自动部署。更简单适合持续部署的SaaS项目。分支命名:feature/xxx、bugfix/xxx、hotfix/xxx。Commit规范:type(scope): description(如feat(user): add login)。PR Review:至少一人审查、CI通过后才能合。保护分支:禁止直接push到main，必须通过PR。Squash and Merge保持历史干净。",
    "Git Flow main/develop/feature/release/hotfix、GitHub Flow main+PR、分支命名规范、Squash and Merge、保护分支", 2,
    "你们团队用哪种分支策略？遇到过什么分支管理的坑？", [50,57]))

Q.append(("什么是分布式事务？Seata的AT模式和TCC模式分别怎么实现？",
    "分布式事务:跨多个数据库/服务的操作要么全部成功要么全部回滚。Seata AT模式:一阶段各分支各自提交并注册undo_log→二阶段全局提交(异步删undo)或回滚(用undo_log逆向补偿)。无侵入(业务代码不改)，依赖数据库本地事务+undo_log。TCC模式:Try(预留资源)→Confirm(确认执行)→Cancel(取消释放)。需业务代码每个分支实现三个方法，侵入大但性能好无锁。SAGA模式:长事务拆分为本地事务链，失败反向补偿。选择:AT适合微服务+关系型DB; TCC适合对性能要求高的核心链路; SAGA适合长流程(订单-库存-物流)。",
    "Seata AT、undo_log、二阶段提交/回滚、TCC Try/Confirm/Cancel、SAGA补偿、无侵入vs有侵入", 3,
    "Seata AT模式和XA两阶段提交有什么区别？为什么AT的性能比XA好？", [53,52]))

# 补充一些 CS 基础和数据结构的独立题目
Q.append(("请介绍进程调度算法:FCFS、SJF、RR、优先级调度和多级反馈队列。",
    "FCFS(先来先服务):非抢占，简单但平均等待时间长(护航效应——长进程堵住短进程)。SJF(最短作业优先):抢占(最短剩余时间优先SRTF)和非抢占，平均等待时间最优但需预知CPU执行时间(实际难预测)。RR(时间片轮转):抢占式，固定时间片轮流执行，时间片太小→上下文切换过多，太大→退化为FCFS。优先级调度:按优先级分配CPU，低优先级可能饿死(老化aging解决)。多级反馈队列(MFQ):多个不同优先级的RR队列，高优先级短时间片低优先级长时间片——结合RR响应快+SJF吞吐高，Linux/Windows都用MFQ变体。",
    "FCFS护航效应、SJF最优等待、RR时间片、优先级老化、多级反馈队列MFQ、抢占vs非抢占", 2,
    "Linux CFS完全公平调度器是怎样实现的？和MFQ有什么不同？", [48]))

# ---- 填充零题目标签 (PHP/Hibernate/Maven/Gradle/Oracle/RocketMQ/ZooKeeper/Angular) ----
Q.append(("PHP中Composer的作用是什么？Laravel框架的核心特性有哪些？",
    "Composer:PHP依赖管理工具，类似Maven/npm。通过composer.json声明依赖，composer.lock锁定版本。Autoload:PSR-4规范自动加载类。Laravel核心特性:(1)Eloquent ORM——优雅的ActiveRecord实现; (2)Blade模板引擎——轻量高效; (3)Artisan CLI——代码生成/迁移/定时任务; (4)中间件——请求过滤链(鉴权/日志/CORS); (5)队列——支持Redis/Beanstalkd驱动异步任务; (6)依赖注入容器——自动解析类依赖。Laravel是PHP最流行框架适合快速开发RESTful API和Web应用。",
    "Composer依赖管理、PSR-4自动加载、Eloquent ORM、Blade模板、Artisan CLI、中间件、队列", 2,
    "Laravel的Eloquent和Doctrine有什么区别？ActiveRecord vs DataMapper模式？", [10]))

Q.append(("Hibernate中一级缓存和二级缓存的区别？N+1问题是什么？如何解决？",
    "一级缓存:Session级别，同一Session内相同查询只查一次DB，默认开启。二级缓存:SessionFactory级别跨Session共享，需配置Ehcache/Hazelcast/Redis，实体加@Cacheable。N+1问题:查父实体(1次SQL)→遍历子实体时每个父实体再发SQL查其子集合(N次SQL)。解决:(1)JOIN FETCH一条SQL关联查询; (2)@BatchSize批量加载(IN查询); (3)EntityGraph声明式加载策略。建议默认LAZY避免连锁JOIN。OSIV(Open Session In View):View层保持Session打开但可能导致长事务和DB连接占用。",
    "一级缓存Session、二级缓存SessionFactory、N+1问题、JOIN FETCH、@BatchSize、EntityGraph、LAZY加载、OSIV", 3,
    "Hibernate OSIV反模式是什么？为什么Spring Boot默认开启却很多人反对？", [16,15]))

Q.append(("Maven依赖传递和冲突解决机制？dependencyManagement的作用？",
    "依赖传递:通过pom继承自动引入间接依赖。scope影响传递:compile(编译运行测试都传递)、provided(不传递如servlet-api)、runtime(运行时传递)、test(不传递)。冲突解决:就近原则(路径短的版本优先); 先声明优先(同层级); exclusions排除传递依赖; dependencyManagement统一管理版本(仅声明不实际引入，子模块用时加dependency且可不写version)。mvn dependency:tree查看完整依赖树排查冲突。BOM集中定义一组依赖版本供多项目引用。",
    "依赖传递、scope传递规则、就近原则、exclusions排除、dependencyManagement统一版本、dependency:tree、BOM", 2,
    "Maven中依赖仲裁(Dependency Mediation)是怎么工作的？实际项目怎么排查冲突？", [17]))

Q.append(("Gradle相比Maven的优势？Gradle的增量构建原理？",
    "优势:(1)DSL脚本Groovy/Kotlin更灵活(编程式而非XML声明式); (2)增量构建——只编译变更源文件和受影响的类; (3)构建缓存跨项目共享(远程缓存CI加速); (4)Daemon守护进程复用JVM热启动; (5)依赖解析更灵活(动态版本、版本冲突策略)。增量构建原理:Gradle用Task Inputs/Outputs的快照跟踪文件变化→只有inputs变化才重新执行task→跳过无变化的task提升构建速度。适用大型多模块项目(Android默认Gradle)。Maven适合传统简单项目。",
    "DSL脚本、增量构建input/output快照、构建缓存、Daemon守护进程、动态版本", 2,
    "从Maven迁移到Gradle有哪些注意事项？什么情况不建议迁移？", [18,17]))

Q.append(("Oracle数据库相比MySQL在架构和企业特性上有哪些主要差异？",
    "架构差异:Oracle表空间+数据文件管理(MySQL一个实例多个库); Oracle UNDO表空间回滚段(MySQL InnoDB UNDO log); Oracle RAC多节点共享存储高可用(MySQL主从/Group Replication); Oracle DataGuard物理/逻辑备库灾备更成熟。企业特性:分区表更丰富(Hash/Range/List/Composite/Reference); 物化视图预计算查询结果; 高级压缩HCC; 资源管理器精细控制CPU/IO; PL/SQL比MySQL存储过程更强大。Oracle收费昂贵适合金融/电信，MySQL免费适合互联网。",
    "表空间、UNDO表空间、RAC多节点共享存储、DataGuard灾备、物化视图、PL/SQL、分区表", 2,
    "Oracle的MVCC和MySQL InnoDB的MVCC实现有什么不同？", [25,20]))

Q.append(("RocketMQ事务消息原理？和Kafka事务、RabbitMQ事务有什么区别？",
    "RocketMQ事务:Producer发half消息(消费者不可见)→执行本地事务→commit(可见)或rollback→长时间未确认Broker回调checkLocalTransaction回查。vs Kafka事务:Kafka保证exactly-once写入(原子写多分区)和read-process-write模式需transaction.id。vs RabbitMQ:通过channel.txSelect开启事务(channel.txCommit/txRollback)性能差，生产多用publisher confirm替代。RocketMQ顺序消息:同业务ID发同一MessageQueue(FIFO)。适用分布式事务场景(订单+扣库存原子性)。",
    "half半消息、本地事务、commit/rollback、回查、分布式事务、顺序消息同MessageQueue、exactly-once", 3,
    "RocketMQ事务消息和Seata AT模式分别适用什么场景？", [29,52,27]))

Q.append(("ZooKeeper的ZAB协议和选举机制？为什么ZK适合做分布式协调？",
    "ZAB原子广播协议保证分布式数据一致性。两种模式:(1)崩溃恢复——Leader选举(ZXID大的节点优先成为Leader); (2)消息广播——Leader将事务提案发给Follower，过半ACK后Commit所有节点提交。ZK保证CP(一致性+分区容忍)，选举期间短暂不可用。适用:分布式锁(临时顺序节点+Watch)、配置中心(Dubbo服务注册)、选主。核心是内存文件系统树+Watcher通知。vs Etcd:Raft协议更易理解，Etcd在K8s领域更流行(K8s弃ZK选Etcd因其运维复杂度低)。",
    "ZAB原子广播、Leader选举ZXID最大、过半ACK、临时顺序节点、Watch通知、CP、Etcd Raft对比", 3,
    "ZooKeeper和Etcd在一致性协议和实际使用上有什么区别？为什么K8s弃ZK选Etcd？", [33,53]))

Q.append(("Angular的依赖注入(DI)原理和模块化架构是怎样的？",
    "DI:Angular内置Injector容器，@Injectable()声明可注入服务，构造函数中注入。层级注入器:ModuleInjector→ElementInjector(每个DOM元素可有独立注入器)。providers:providedIn:root单例全局; 组件providers组件级实例。模块化:@NgModule声明组件/服务/管道/指令; imports引入其他模块; exports导出; bootstrap启动根组件。特性模块懒加载(路由loadChildren)+Standalone Component(Angular14+独立组件无需NgModule)。RxJS流式处理异步数据(Observable+pipe+operators)。vs React:Angular DI更完善，React用Hooks+Context模式替代。",
    "@Injectable、Injector、层级注入器、@NgModule、懒加载、Standalone Component、RxJS Observable", 2,
    "Angular的Standalone Component相比@NgModule有什么优势？是否应该全面迁移？", [39,46]))

# ================================================================
# SQL 生成逻辑
# ================================================================

def esc(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"""-- ============================================================
-- 智面幻境 · 技能标签题库
-- {len(TAGS)} 标签 × {len(Q)} 题（含详细参考答案）
-- 用法1: mysql -u root -p zhimian < seed_skill_bank.sql
-- 用法2: Navicat → 打开本文件 → 点击"运行"按钮 → 等待完成
-- 幂等：可重复执行（开头有 DROP IF EXISTS）
-- ============================================================

USE zhimian;
DROP TABLE IF EXISTS skill_question_tag_rel;
DROP TABLE IF EXISTS skill_question;
DROP TABLE IF EXISTS skill_tag;

CREATE TABLE skill_tag (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '标签名称',
    category VARCHAR(50) COMMENT '所属分类',
    description TEXT COMMENT '标签简介',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序权重',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='技能标签表';

CREATE TABLE skill_question (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '题目ID',
    content TEXT NOT NULL COMMENT '题干',
    reference_answer TEXT NOT NULL COMMENT '参考答案(详细版)',
    answer_keywords TEXT COMMENT '答案关键词(、分隔)',
    difficulty TINYINT NOT NULL DEFAULT 2 COMMENT '难度:1入门 2中等 3困难',
    followup_guide TEXT COMMENT '追问引导(面试官可选追问方向)',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_difficulty (difficulty)
) ENGINE=InnoDB COMMENT='技能题目表';

CREATE TABLE skill_question_tag_rel (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    question_id BIGINT NOT NULL COMMENT '题目ID',
    tag_id BIGINT NOT NULL COMMENT '标签ID',
    UNIQUE KEY uk_qt (question_id, tag_id),
    KEY idx_tag (tag_id)
) ENGINE=InnoDB COMMENT='题目-标签关联表(多对多)';

-- ============================================================
-- 插入 {len(TAGS)} 个技能标签
-- ============================================================
""")
    for tid, name, cat, desc in TAGS:
        f.write(f"INSERT INTO skill_tag (id, name, category, description, sort_order) VALUES ({tid}, '{esc(name)}', '{esc(cat)}', '{esc(desc)}', {tid});\n")

    f.write(f"\n-- ============================================================\n-- 插入 {len(Q)} 道题目\n-- ============================================================\n")
    for i, (content, answer, keywords, diff, followup, _) in enumerate(Q, 1):
        f.write(f"INSERT INTO skill_question (id, content, reference_answer, answer_keywords, difficulty, followup_guide) VALUES ({i}, '{esc(content)}', '{esc(answer)}', '{esc(keywords)}', {diff}, '{esc(followup)}');\n")

    f.write(f"\n-- ============================================================\n-- 题目-标签关联（多对多，约{sum(len(q[5]) for q in Q)}条）\n-- ============================================================\n")
    for i, q in enumerate(Q, 1):
        for tid in q[5]:
            f.write(f"INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES ({i}, {tid});\n")

    f.write("""
-- ============================================================
-- 校验查询（可在 Navicat 中单独执行）
-- ============================================================

-- 查看所有标签：   SELECT * FROM skill_tag ORDER BY sort_order;

-- 每个标签下的题目数：
-- SELECT t.id, t.name AS 标签名, COUNT(r.question_id) AS 题目数
-- FROM skill_tag t LEFT JOIN skill_question_tag_rel r ON t.id = r.tag_id
-- GROUP BY t.id, t.name ORDER BY t.sort_order;

-- 总题目数：       SELECT COUNT(*) AS 总题目数 FROM skill_question;
-- 总关联数：       SELECT COUNT(*) AS 总关联数 FROM skill_question_tag_rel;
-- 多标签题目数：   SELECT COUNT(*) AS 多标签题目数 FROM (SELECT question_id FROM skill_question_tag_rel GROUP BY question_id HAVING COUNT(*)>1) t;

-- 查询某标签下的所有题目（例如 Java，tag_id=1）：
-- SELECT sq.id, sq.content, sq.reference_answer, sq.difficulty, sq.followup_guide
-- FROM skill_question sq
-- JOIN skill_question_tag_rel r ON sq.id = r.question_id
-- WHERE r.tag_id = 1 ORDER BY sq.difficulty, sq.id;

-- 查询同时属于 Java(1) 和 MySQL(20) 的题目（多标签重合）：
-- SELECT sq.id, sq.content FROM skill_question sq
-- JOIN skill_question_tag_rel r1 ON sq.id = r1.question_id AND r1.tag_id = 1
-- JOIN skill_question_tag_rel r2 ON sq.id = r2.question_id AND r2.tag_id = 20;
""")

# 统计
multi_count = sum(1 for q in Q if len(q[5]) > 1)
tag_count = {}
for q in Q:
    for tid in q[5]:
        tag_count[tid] = tag_count.get(tid, 0) + 1

print(f"✅ SQL 生成完成！")
print(f"   标签: {len(TAGS)} 个")
print(f"   题目: {len(Q)} 道")
print(f"   关联: {sum(len(q[5]) for q in Q)} 条")
print(f"   多标签题: {multi_count}/{len(Q)} ({multi_count*100//len(Q)}%)")
print(f"   文件: {OUT}")
print(f"   大小: {os.path.getsize(OUT)/1024:.1f} KB")
print()
print("   各标签题目数:")
for t in TAGS:
    cnt = tag_count.get(t[0], 0)
    print(f"     {t[1]:<20s} {cnt:>3d} 题", end="")
    if cnt == 0:
        print(" ⚠️ 缺题!")
    else:
        print()
