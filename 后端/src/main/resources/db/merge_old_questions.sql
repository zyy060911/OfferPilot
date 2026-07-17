-- ============================================================
-- 旧题库迁移脚本：question → skill_question + skill_question_tag_rel
-- ============================================================
USE zhimian;

-- Step 1: 补充旧题库需要的标签（若不存在）
INSERT IGNORE INTO skill_tag (id, name, category, description, sort_order) VALUES
(58, '浏览器', '前端', '浏览器渲染原理、重排重绘、缓存机制、DevTools、跨域', 58),
(59, '性能优化', '工程实践', '性能优化：首屏加载、懒加载、CDN、缓存策略、SQL优化、GC调优', 59),
(60, '项目经验', '工程实践', '项目架构设计、技术选型、难点解决、团队协作、复盘总结', 60);

-- Step 2: 插入 25 道旧题到 skill_question（带完整参考答案）
INSERT INTO skill_question (content, reference_answer, answer_keywords, difficulty, followup_guide) VALUES
('请谈谈 Java 中 == 和 equals 的区别，以及为什么重写 equals 时通常要重写 hashCode？',
 '== 比较栈中引用地址(基本类型比值)。equals()在 Object 中默认用 == 比较，子类如 String 重写为值比较。重写 equals 必须重写 hashCode 因为 Java 规范要求:equals 相等的两个对象 hashCode 必须相等，否则在 HashMap/HashSet 等哈希容器中，逻辑相同的 key 会落在不同桶中导致查找失败。Object.hashCode() 是 native 方法返回与内存地址相关的值，不保证逻辑一致性。实际例子:用自定义对象作 HashMap key，只重写 equals 不重写 hashCode，同一个逻辑 key 存进去后却 get 不到。',
 '引用比较、值比较、Object默认实现、哈希一致性、equals相等则hashCode必须相等、HashMap查找失败', 1,
 '能举一个不重写 hashCode 导致 HashMap 行为异常的具体例子吗？'),

('说说 Java 的基本数据类型有哪些，以及自动装箱拆箱可能带来的问题。',
 '八种基本类型:byte、short、int、long、float、double、char、boolean。对应包装类:Byte、Short、Integer、Long、Float、Double、Character、Boolean。自动装箱:编译器将基本类型自动转为包装类(如 Integer i=100 相当于 Integer.valueOf(100))。自动拆箱:包装类自动转基本类型(如 int j=i 相当于 i.intValue())。常见问题:(1)包装类可为 null，自动拆箱时抛出 NullPointerException;(2)频繁装箱创建对象有性能开销和GC压力;(3)Integer 缓存池默认 -128~127，超出此范围的 == 比较引用地址返回 false;(4)集合只能存对象，基本类型需装箱增加开销。',
 '八种基本类型、包装类、装箱拆箱、缓存池-128到127、NPE、性能开销、==与equals', 1,
 'Integer 缓存范围可以调整吗？怎么通过 JVM 参数扩大？'),

('请描述一下 JVM 的内存区域划分，以及哪些区域是线程私有的。',
 '线程私有区域:(1)程序计数器(PC Register):当前线程执行字节码的行号指示器;(2)虚拟机栈(VM Stack):每个方法执行创建栈帧，存储局部变量表、操作数栈、动态链接、返回值;(3)本地方法栈:为 Native 方法服务。线程共享区域:(1)堆(Heap):存放对象实例和数组，GC 主要区域，分为新生代(Eden+S0+S1)和老年代;(2)方法区/MetaSpace(JDK8+):存储类信息、常量、静态变量、JIT 编译后的代码缓存，使用本地内存避免 PermGen OOM。',
 '程序计数器、虚拟机栈栈帧、本地方法栈、堆、方法区/MetaSpace、线程私有、新生代Eden Survivor、老年代', 2,
 'JDK8 为什么用 MetaSpace 替代永久代？MetaSpace 会 OOM 吗？'),

('谈谈 JVM 的垃圾回收机制，常见的垃圾回收算法和你了解的收集器。',
 '判断对象存活:可达性分析(从 GC Roots 出发的引用链)。三种基础算法:(1)标记-清除:标记存活→清除未标记，简单但有内存碎片;(2)标记-复制:存活对象复制到另一块→清空当前块，无碎片但内存利用率50%，适合新生代(HotSpot Eden:S0:S1=8:1:1);(3)标记-整理:存活对象移动到一端→清理边界外，无碎片且利用率高，需要 STW。经典收集器:Serial(单线程)、Parallel(吞吐优先)、CMS(并发低延迟但碎片)、G1(Region+并发标记+复制，平衡延迟和吞吐)、ZGC/Shenandoah(亚毫秒级暂停)。实际组合:新生代用复制(Parallel Scavenge)，老年代用整理(Parallel Old)或 CMS/G1 并发收集。',
 '可达性分析、标记清除碎片、标记复制Eden:Survivor=8:1:1、标记整理STW、Serial、Parallel、CMS、G1、ZGC', 3,
 '你在项目中调过 GC 参数吗？是怎么观察 GC 日志并做优化的？'),

('请比较 ArrayList 和 LinkedList 的区别及各自的适用场景。',
 'ArrayList:底层动态数组(Object[])，随机访问 O(1)，尾部插入 O(1)均摊(扩容时 O(n))，中间插入/删除 O(n)(需移动后续元素)。内存紧凑利于 CPU 缓存。LinkedList:底层双向链表，插入删除 O(1)(已定位到节点时)，随机访问 O(n)(需从头或尾遍历)。每个节点有前后指针+数据，内存开销大。适用场景:ArrayList 适合随机访问多、尾部增删、读多写少的场景(绝大多数业务场景);LinkedList 适合频繁头尾插入删除的场景(如作为队列/双端队列使用时)。实际项目中几乎都用 ArrayList(LinkedList 即使插入也不一定更快——先要 O(n) 遍历找到插入位置)。',
 '动态数组ArrayList、双向链表LinkedList、随机访问O(1) vs O(n)、中间插入O(n)、缓存友好、ArrayList默认优先', 1,
 '在频繁头部插入的场景下你会选 ArrayList 还是 LinkedList？为什么？'),

('说说 HashMap 的底层数据结构和扩容机制，JDK1.8 做了哪些改进。',
 '底层:数组(Node[])+链表+红黑树。put 流程:(1)key.hashCode()→扰动函数(高16位异或低16位);(2)(n-1)&hash 得数组下标;(3)该位置为空直接插入;不为空→(4)判断 key 是否相同(hash相等+==或equals)→相同则覆盖;(5)若链表→遍历插入(链表长度>=8且数组容量>=64转为红黑树);(6)size>threshold(容量*负载因子0.75)→扩容容量翻倍→原链表拆分:e.hash&oldCap==0 在原位置，!=0 在原位置+oldCap。JDK8 改进:(1)链表→红黑树(O(n)→O(logn));(2)头插法→尾插法(避免并发扩容死循环/环形链表);(3)简化扰动函数(高16位异或低16位一次)。',
 '数组+链表+红黑树、扰动函数、(n-1)&hash定位、负载因子0.75、扩容翻倍、树化阈值8/64、尾插法避免死循环', 2,
 '为什么链表转红黑树的阈值是 8？退化链表阈值为什么是 6？'),

('请解释一下 Java 中线程的几种创建方式，以及线程池的核心参数。',
 '创建方式:(1)继承 Thread 类重写 run();(2)实现 Runnable 接口;(3)实现 Callable 接口+FutureTask(Future 有返回值可抛异常);(4)线程池 Executors(推荐)。线程池核心参数(ThreadPoolExecutor):(1)corePoolSize 核心线程数;(2)maximumPoolSize 最大线程数;(3)keepAliveTime+unit 非核心线程空闲存活时间;(4)workQueue 工作队列(LinkedBlockingQueue 无界/SynchronousQueue 无缓冲/ArrayBlockingQueue 有界);(5)threadFactory 线程工厂;(6)RejectedExecutionHandler 拒绝策略:Abort 抛异常/CallerRuns 调用者执行/Discard 丢弃/DiscardOldest 丢最旧。推荐手动 new ThreadPoolExecutor 而非用 Executors 快捷方法(避免 OOM)。',
 'Thread、Runnable、Callable+FutureTask、ThreadPoolExecutor、核心线程数、最大线程数、阻塞队列、拒绝策略、禁止Executors快捷方法', 2,
 '你在项目中用线程池处理过什么任务？拒绝策略选的哪种为什么？'),

('谈谈 synchronized 和 ReentrantLock 的区别，以及 volatile 的作用。',
 'synchronized:(1)Java 内置关键字，JVM 层面实现;(2)自动加锁释放(代码块退出/异常);(3)非公平锁;(4)JDK6+ 有锁升级(偏向锁→轻量级锁/CAS→重量级锁);(5)等待不可中断;(6)不支持条件变量。ReentrantLock:(1)java.util.concurrent.locks 下的类;(2)手动 lock()/unlock()(finally 释放);(3)可选公平锁;(4)可中断等待 lockInterruptibly();(5)支持 Condition 条件变量(signal/await);(6)tryLock(timeout)超时获取。volatile:(1)保证可见性——修改立即可见于其他线程;(2)禁止指令重排序(内存屏障);(3)不保证原子性——i++ 复合操作仍不安全(读-改-写三步可能被打断)。',
 'synchronized内置锁、锁升级偏向轻量重量、ReentrantLock手动释放公平锁、tryLock超时、volatile可见性有序性不保证原子性、内存屏障', 3,
 'volatile 能保证原子性吗？为什么 i++ 用 volatile 还是线程不安全的？'),

('请说明 Spring Boot 自动配置的原理。',
 '@SpringBootApplication 包含 @EnableAutoConfiguration，后者通过 @Import(AutoConfigurationImportSelector.class) 导入选择器。AutoConfigurationImportSelector 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports 文件(Spring Boot 3.x)，加载所有自动配置类。每个配置类通过条件注解判断是否生效:@ConditionalOnClass(类存在)、@ConditionalOnBean(Bean存在)、@ConditionalOnProperty(配置匹配)、@ConditionalOnMissingBean(用户未自定义才生效)。满足条件则创建 Bean 注入容器。自定义 Starter:创建 autoconfigure 模块(写 @Configuration 类+条件注解+@ConfigurationProperties)和 starter 模块(空模块引入依赖)，实现零配置开箱即用。',
 '@EnableAutoConfiguration、AutoConfigurationImportSelector、AutoConfiguration.imports、@ConditionalOnClass、@ConditionalOnMissingBean、自定义Starter', 2,
 '能结合你的项目说明自动配置解决了什么问题吗？@ConditionalOnMissingBean 有什么坑？'),

('说说 Spring 中 Bean 的生命周期，以及如何解决循环依赖。',
 'Bean 生命周期:实例化(构造器)→属性填充(@Autowired 注入)→Aware 回调(BeanNameAware/BeanFactoryAware/ApplicationContextAware)→BeanPostProcessor 前置处理→初始化(@PostConstruct→InitializingBean.afterPropertiesSet→init-method)→BeanPostProcessor 后置处理(AOP 代理在此生成)→Bean 就绪→容器关闭时销毁(@PreDestroy→DisposableBean.destroy→destroy-method)。循环依赖解决:Spring 三级缓存——(1)singletonObjects:完全初始化好的单例 Bean;(2)earlySingletonObjects:提前暴露的半成品 Bean 引用;(3)singletonFactories:产生提前引用的 ObjectFactory。流程:A 实例化→暴露工厂到三级缓存→属性填充发现需要 B→B 实例化→B 属性填充发现需要 A→从三级缓存拿到 A 的提前引用→B 完成→A 完成。构造器注入无法解决循环依赖(因为必须先获取完全初始化的 Bean)。',
 '实例化、属性填充、初始化、三级缓存singletonObjects/earlySingletonObjects/singletonFactories、提前暴露、构造器注入无法解决循环依赖', 3,
 '三级缓存中第三级缓存存的是什么？只有两级行不行？'),

('请谈谈数据库索引的原理，以及什么情况下索引会失效。',
 '索引使用 B+Tree 数据结构:非叶子节点存索引 key，叶子节点存完整行数据(聚簇索引)或主键值(二级索引需回表)，叶子节点双向链表连接支持范围查询。一个 16KB 页可存约 1170 个 key，3 层索引约 2000 万行仅 3 次磁盘 IO。覆盖索引:查询字段全在索引中→不用回表。索引失效场景:(1)违反最左前缀——联合索引(a,b,c)查询条件缺 a;(2)对索引列使用函数(YEAR(col));(3)隐式类型转换(varchar 列 WHERE phone=13800138000);(4)LIKE 以 % 开头;(5)OR 条件中有非索引列;(6)!= 或 <>;(7)IS NULL/IS NOT NULL(视优化器)。排查:用 EXPLAIN 看 type/rows/Extra 确认是否走索引。',
 'B+Tree、16KB页、三层层2000万行3次IO、聚簇索引、二级索引回表、覆盖索引、最左前缀、索引失效、EXPLAIN', 2,
 '你在项目里遇到过慢查询吗？怎么用 EXPLAIN 分析并优化的？'),

('说说 MySQL 的事务隔离级别，以及如何解决幻读。',
 '四种隔离级别:(1)READ UNCOMMITTED——可读未提交数据，脏读/不可重复读/幻读都存在;(2)READ COMMITTED——只读已提交数据，解决脏读(RC 每次快照读生成新 ReadView);(3)REPEATABLE READ(InnoDB 默认)——同一事务多次读取结果一致，解决脏读+不可重复读(使用同一个 ReadView);(4)SERIALIZABLE——读加共享锁写加排他锁，完全串行，解决所有问题但性能最差。幻读解决:InnoDB 在 RR 级别引入间隙锁(Gap Lock)——锁定索引记录间的间隙，防止其他事务插入新记录到该范围。临键锁(Next-Key Lock)=记录锁(Record Lock)+间隙锁(Gap Lock)。但并非完全杜绝幻读——SELECT...FOR UPDATE 的最新读仍可能出现幻影行(因为锁定范围外的插入)。',
 '读未提交、读已提交RC、可重复读RR、串行化、MVCC、ReadView、间隙锁Gap Lock、临键锁Next-Key Lock、脏读、不可重复读、幻读', 3,
 'InnoDB 在 RR 级别下是怎么用间隙锁避免幻读的？什么情况下仍可能幻读？'),

('谈谈 Redis 常见的数据类型及其典型应用场景。',
 '五种基本类型:(1)String(SDS):SET/GET/INCR/DECR/SETNX。场景:缓存 JSON、计数器(INCR 原子自增)、分布式锁(SET key value NX EX)、限流滑动窗口。(2)Hash:ziplist/hashtable，HMSET/HGETALL。场景:对象存储可部分更新，比 String 存整个 JSON 省空间。(3)List:quicklist，LPUSH/RPOP/BRPOP。场景:消息队列、最新动态列表(LPUSH+LTRIM 保留最近 N 条)。(4)Set:hashtable，SADD/SINTER/SUNION。场景:标签、共同好友(交集)、抽奖去重。(5)ZSet:skiplist+hashtable，ZADD/ZRANGEBYSCORE。场景:排行榜、延迟队列(score=执行时间戳)。高级类型:Bitmap(签到统计)、HyperLogLog(UV 统计)、Geo(附近的人)、Stream(持久化 MQ)。',
 'String、Hash、List、Set、ZSet、skiplist、quicklist、排行榜、延迟队列、分布式锁、UV统计', 1,
 'ZSet 底层为什么用跳表而不用红黑树？跳表有什么优势？'),

('请说明 Redis 缓存穿透、缓存击穿、缓存雪崩的区别和解决方案。',
 '缓存穿透:查询 DB 不存在的数据→缓存无→大量请求直击 DB。解决:(1)布隆过滤器——预判 key 一定不存在则直接返回;(2)缓存空值——null 也缓存，短过期时间(3-5分钟);(3)前端参数校验拦截非法 id。缓存击穿:热点 key 过期瞬间大量并发打到 DB。解决:(1)互斥锁/分布式锁——第一个请求获取锁查 DB 写缓存，其余等待;(2)逻辑过期——缓存永不过期+异步线程定期更新;(3)热点 key 直接永不过期。缓存雪崩:大量 key 同时过期或 Redis 宕机。解决:(1)过期时间加随机值(+/-30% 打散);(2)Redis 高可用(主从+哨兵/Cluster);(3)多级缓存(本地 Caffeine+Redis);(4)限流降级保护 DB。',
 '缓存穿透、布隆过滤器、缓存空值、缓存击穿、互斥锁、逻辑过期、缓存雪崩、过期时间打散、多级缓存、限流降级', 2,
 '布隆过滤器的原理是什么？为什么它会有误判？误判率怎么计算？'),

('请介绍一个你最有成就感的后端项目，重点说明你负责的模块和解决的关键技术难点。',
 '这是开放性面试题，考察项目经验和表达能力。回答框架:(1)项目背景——业务场景、用户规模、技术栈;(2)个人职责——你具体负责了哪些模块(不要说我参与了全部);(3)遇到的关键难点——如高并发下数据一致性保证、慢查询从10s优化到0.1s、分布式事务选型;(4)解决方案——具体技术方案和决策理由;(5)量化成果——QPS 提升了多少、P99 延迟降低了多少。加分项:提及失败经历和复盘改进、如何推动方案在团队落地。面试官重点在听:问题分析能力(是否抓到根因)、技术深度(原理层面)、工程思维(不只是调API)。',
 '项目背景、个人职责、技术难点、解决方案、量化成果、失败复盘、问题分析能力、技术深度、工程思维', 2,
 '这个项目中遇到的最大性能瓶颈是什么？你是怎么定位并解决的？如果现在重新设计会怎么做？'),

-- 前端 10 题
('请谈谈 CSS 盒模型，以及标准盒模型和怪异盒模型的区别。',
 'CSS 盒模型:每个元素看作矩形盒子，由内到外 content(内容)+padding(内边距)+border(边框)+margin(外边距)。标准盒模型(W3C):box-sizing:content-box(默认)。width/height 仅指 content 区域，实际占用=width+padding+border。怪异盒模型(IE):box-sizing:border-box。width/height=content+padding+border 总和，设置宽高后内容自动缩小。border-box 更符合直觉也更实用——设置完宽度后加 padding 不会撑大盒子。现代开发普遍全局设置 *{box-sizing:border-box;}。',
 'content、padding、border、margin、标准盒模型content-box、怪异盒模型border-box、全局设置border-box', 1,
 '实际开发中你一般把 box-sizing 设成什么？为什么 border-box 更省心？'),

('说说常见的 CSS 居中方案，以及 flex 布局的核心属性。',
 '水平居中:行内 text-align:center; 块级 margin:0 auto。垂直居中:单行文字 line-height=容器高度。未知宽高绝对居中:position:absolute+top:50%+left:50%+transform:translate(-50%,-50%)。Flex 居中:display:flex+justify-content:center+align-items:center(最简洁方案)。Flex 核心:容器 display:flex/flex-direction/justify-content/align-items/flex-wrap/gap; 子项 flex-grow(放大比例)/flex-shrink(缩小)/flex-basis(初始尺寸)/flex 简写(flex:1=1 1 0%)。',
 'text-align:center、margin:0 auto、absolute+transform、flex+justify-content+align-items、flex-grow/shrink/basis、flex:1', 2,
 '一个未知宽高的元素要水平垂直居中，你会优先用哪种方案？为什么？'),

('请解释 JavaScript 中的闭包，以及它的常见应用和潜在问题。',
 '闭包:函数有权访问其外部作用域中的变量，即使外部函数已执行完毕。内部函数持有对外部变量引用，变量不会被 GC 回收。常见应用:(1)数据私有化——模块模式创建私有变量;(2)函数柯里化——预设参数的函数工厂;(3)回调/事件处理——保留上下文数据;(4)防抖节流——在闭包中保存 timer 变量。潜在问题:(1)内存泄漏——闭包持有 DOM 引用导致已移除的 DOM 无法回收;(2)循环 var 陷阱——循环中所有闭包共享同一个 var 变量(let 块级作用域解决);(3)过度使用占用内存。解决:闭包引用置 null 及时释放; 用 WeakMap 存弱引用。',
 '外部变量被持有、数据私有化、柯里化、防抖节流、内存泄漏、循环var陷阱、let块级作用域、WeakMap', 2,
 '在项目中哪用到过闭包？怎么避免内存泄漏的？'),

('谈谈 JavaScript 的事件循环机制，宏任务和微任务的执行顺序。',
 'JS 单线程，事件循环是异步编程核心。流程:(1)同步代码进调用栈执行;(2)异步操作(setTimeout/Promise)交给 Web API 处理;(3)完成后回调进任务队列;(4)调用栈空时，事件循环取回调。宏任务:script 整体、setTimeout、setInterval、I/O、UI rendering——每次循环取一个宏任务。微任务:Promise.then/catch/finally、MutationObserver、queueMicrotask——宏任务执行完后清空所有微任务(微任务产生的新微任务也会在本轮清空)。执行顺序:同步代码→清空微任务→下一宏任务。async/await 中 await 后续代码等同于 Promise.then 进入微任务。',
 '单线程、调用栈、Web API、宏任务setTimeout、微任务Promise.then、微任务优先清空、async/await=Promise语法糖', 3,
 '能口述一段含 Promise 和 setTimeout 的代码的输出顺序并解释为什么吗？'),

('说说 var、let、const 的区别，以及什么是变量提升和暂时性死区。',
 'var:函数作用域(非块级)，可重复声明，存在变量提升(声明提升初始值 undefined)。let:块级作用域({}内有效)，不可重复声明，存在暂时性死区(TDZ——声明前访问抛 ReferenceError)。const:块级作用域，声明时必须赋初始值，不可重新赋值(但对象属性可修改——const 锁定引用而非值)。变量提升:JS 引擎执行前将 var 声明和 function 整体提升到作用域顶部。TDZ:let/const 从块作用域开始到声明的区域，此时访问会报错。推荐:默认用 const，需要重新赋值用 let，不使用 var。',
 '函数作用域vs块级作用域、变量提升初始undefined、暂时性死区TDZ、const锁定引用、对象属性可修改', 1,
 'const 声明的对象，其属性可以修改吗？为什么？如果要对象完全不可变怎么做？'),

('请说明 Vue 的响应式原理，Vue2 和 Vue3 在实现上有什么不同。',
 'Vue2:Object.defineProperty() 劫持属性 getter/setter。getter 中依赖收集(Dep.target+dep.depend)，setter 中派发更新(dep.notify→Watcher→重新渲染)。局限:无法监听数组索引修改和 length 变化(需 Vue.set/delete 或重写 7 个数组方法 push/pop/shift/unshift/splice/sort/reverse);无法监听属性新增/删除;需递归遍历所有属性初始化(深层对象性能差)。Vue3:Proxy 代理整个对象——属性读写、新增删除、数组索引修改都能拦截。ref 用 getter/setter 处理基本类型;reactive 用 Proxy 处理对象/数组。懒代理——仅访问到的深层对象才被代理。优势:(1)检测数组变化;(2)检测属性增删;(3)懒代理性能更好;(4)Proxy 直接代理无需遍历。',
 'Object.defineProperty劫持getter/setter、Dep.target依赖收集、Watcher更新、Vue.set/delete、Proxy全局代理、ref getter/setter、reactive、懒代理', 3,
 'Vue3 用 Proxy 替代 defineProperty 主要解决了哪些痛点？ref 和 reactive 怎么选？'),

('谈谈 Vue 的生命周期钩子，以及 v-if 和 v-show 的区别。',
 '生命周期:beforeCreate→created(数据观测完成，可调 API)→beforeMount→mounted(DOM 挂载完成)→beforeUpdate→updated→beforeUnmount(清理定时器/事件)→unmounted。Vue3 Composition API:setup() 替代 beforeCreate/created，onMounted/onUnmounted 等。v-if:条件为真才渲染 DOM，切换时销毁和重建(触发完整生命周期)，适合不频繁切换(路由/权限控制)。v-show:始终渲染 DOM 通过 display:none 控制显隐，切换开销小但首次渲染不可免，适合频繁切换(标签页/折叠面板)。初始化数据发请求:放在 created 或 mounted(created 数据已可用且比 mounted 早，但 SSR 无 DOM 环境用 created)。',
 'beforeCreate/created、beforeMount/mounted、beforeUpdate/updated、beforeUnmount/unmounted、setup()、v-if销毁重建、v-show display切换', 1,
 '发请求获取初始数据，你一般放在哪个生命周期钩子里？为什么不放更早？'),

('请说说 Vue 中组件之间通信的几种方式。',
 '父子通信:(1)props 父传子(单向数据流);(2)$emit/@事件 子传父。隔代通信:(1)provide/inject——祖先 provide 后代 inject(跨多层级，配合 ref/reactive 实现响应式);(2)slot 插槽——父组件通过 slot 传入内容。全局状态:(1)Pinia(推荐)/Vuex——集中式状态管理;(2)EventBus——小型项目用(mitt 等第三方库)。其他:ref 直接访问子组件实例(紧密耦合不推荐用于业务通信)。推荐方案:父子用 props+emit;全局状态用 Pinia;跨层级用 provide/inject;少用 EventBus 难维护。',
 'props父传子、$emit子传父、provide/inject跨级、slot插槽、Pinia状态管理、EventBus mitt', 2,
 '跨多层级的组件通信你会怎么处理？为什么不用层层 props 传递？'),

('请描述从浏览器输入 URL 到页面展示，中间发生了什么。',
 '完整流程:(1)URL 解析(协议/域名/端口/路径/参数);(2)DNS 解析(浏览器缓存→OS hosts→路由器缓存→递归查询)→获取 IP;(3)TCP 三次握手;(4)HTTPS TLS 握手(如需要);(5)发送 HTTP 请求;(6)服务器处理返回响应;(7)解析 HTML→DOM 树;(8)解析 CSS→CSSOM 树;(9)合并为 Render 树;(10)布局(Layout)——计算位置大小;(11)绘制(Paint)——填充像素;(12)合成(Composite)——分层渲染 GPU 加速;(13)JS 阻塞——遇到 script(非 async/defer)暂停 DOM 解析。关键优化点:DNS 预解析、CDN、资源压缩、关键 CSS 内联、JS 异步加载。',
 'DNS解析、TCP三次握手、TLS握手、DOM/CSSOM/Render树、Layout回流、Paint重绘、Composite合成、JS阻塞、缓存策略', 2,
 '这十几步中哪一步最容易成为性能瓶颈？前端和后端分别能做什么优化？'),

('请谈谈前端性能优化的常见手段，以及你在项目中实践过哪些。',
 '网络优化:(1)CDN 加速;(2)HTTP/2 多路复用;(3)Gzip/Brotli 压缩;(4)浏览器缓存(Cache-Control/ETag)。资源优化:(1)路由懒加载/代码分割;(2)Tree Shaking;(3)图片压缩 WebP/AVIF、响应式图片;(4)字体子集化。渲染优化:(1)关键 CSS 内联;(2)defer/async 延迟 JS;(3)减少回流重绘(transform/opacity GPU 合成层);(4)虚拟列表长列表;(5)防抖节流高频事件。性能监控:Lighthouse 评分、Core Web Vitals(FCP/LCP/CLS)、Performance API。举例:项目首屏 3s→1s:路由懒加载+图片 WebP+CDN+Gzip+组件按需引入(Element Plus unplugin)。',
 'CDN、HTTP/2、Gzip、缓存、代码分割懒加载、Tree Shaking、WebP/AVIF、回流重绘、虚拟列表、Lighthouse、Web Vitals', 2,
 '你的项目首屏加载做过优化吗？优化前后大概提升了多少？具体用了哪些手段？');

-- Step 3: 建立题目-标签关联
-- 先获取这批新插入题目 ID 的起始值
SET @start_id = (SELECT MAX(id) FROM skill_question) - 24;

-- Java后端15题 (id: start~start+14)
-- Q1: == equals hashCode → Java(1)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id, 1);
-- Q2: 基本类型 装箱拆箱 → Java(1), JVM(11)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+1, 1), (@start_id+1, 11);
-- Q3: JVM内存 → JVM(11), Java(1)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+2, 11), (@start_id+2, 1);
-- Q4: GC → JVM(11), Java(1)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+3, 11), (@start_id+3, 1);
-- Q5: ArrayList LinkedList → Java(1), 数据结构(44)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+4, 1), (@start_id+4, 44);
-- Q6: HashMap → Java(1), 数据结构(44)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+5, 1), (@start_id+5, 44);
-- Q7: 线程池 → Java并发(19), Java(1)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+6, 19), (@start_id+6, 1);
-- Q8: synchronized ReentrantLock → Java并发(19), Java(1)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+7, 19), (@start_id+7, 1);
-- Q9: SpringBoot自动配置 → Spring Boot(13), Spring(12)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+8, 13), (@start_id+8, 12);
-- Q10: Bean生命周期 → Spring(12), Spring Boot(13)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+9, 12), (@start_id+9, 13);
-- Q11: 数据库索引 → MySQL(20), SQL(26), 数据结构(44)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+10, 20), (@start_id+10, 26), (@start_id+10, 44);
-- Q12: 事务隔离级别 → MySQL(20), SQL(26)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+11, 20), (@start_id+11, 26);
-- Q13: Redis数据类型 → Redis(22)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+12, 22);
-- Q14: 缓存三大问题 → Redis(22), 分布式系统(53)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+13, 22), (@start_id+13, 53);
-- Q15: 项目经验 → 项目经验(60), 软件工程(57)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+14, 60), (@start_id+14, 57);

-- 前端10题 (id: start+15~start+24)
-- Q16: CSS盒模型 → CSS(36), HTML(35)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+15, 36), (@start_id+15, 35);
-- Q17: CSS居中 Flex → CSS(36)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+16, 36);
-- Q18: JS闭包 → JavaScript(5)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+17, 5);
-- Q19: 事件循环 → JavaScript(5), 浏览器(58)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+18, 5), (@start_id+18, 58);
-- Q20: var let const → JavaScript(5)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+19, 5);
-- Q21: Vue响应式原理 → Vue(37), JavaScript(5)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+20, 37), (@start_id+20, 5);
-- Q22: Vue生命周期 → Vue(37)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+21, 37);
-- Q23: Vue组件通信 → Vue(37)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+22, 37);
-- Q24: URL到页面 → 浏览器(58), 计算机网络(47), HTTP/HTTPS(49)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+23, 58), (@start_id+23, 47), (@start_id+23, 49);
-- Q25: 前端性能优化 → 性能优化(59)
INSERT INTO skill_question_tag_rel (question_id, tag_id) VALUES (@start_id+24, 59);

-- Step 4: 备份旧 question 表
RENAME TABLE question TO question_old;
SELECT 'Old questions migrated to skill_question successfully!' AS result;
