These tools are what I use to analyze monitor runs.

threadpool-usage.sh: This will show you the thread pools in Core that
field incoming requests from the outside, and how much of those pools
are in use.  You give it one or more arguments, each of which is a
file containing one or more thread dumps.  For instance:

    threadpool-usage.sh tomcat-catalina.out

Which would get you an output like this:

2021-04-28 16:49:25
ThreadPool        Used    Total   Utilization
http-bio-127.0.0.1-8081-exec  46      78      58.00
http-bio-127.0.0.1-8082-exec  0      10      0
http-bio-127.0.0.1-8083-exec  45      60      75.00
http-bio-127.0.0.1-8085-exec  15      17      88.00
http-bio-127.0.0.1-8087-exec  16      20      80.00
http-bio-127.0.0.1-8089-exec  3      10      30.00
http-bio-127.0.0.1-8091-exec  0      10      0
http-bio-127.0.0.1-8092-exec  22      24      91.00
http-bio-127.0.0.1-8093-exec  0      3      0
http-nio-127.0.0.1-8084-exec  0      10      0
MIServerWorker  0      30      0

2021-04-28 16:49:30
ThreadPool        Used    Total   Utilization
http-bio-127.0.0.1-8081-exec  51      78      65.00
http-bio-127.0.0.1-8082-exec  0      10      0
http-bio-127.0.0.1-8083-exec  44      60      73.00
http-bio-127.0.0.1-8085-exec  14      17      82.00
http-bio-127.0.0.1-8087-exec  15      20      75.00
http-bio-127.0.0.1-8089-exec  3      10      30.00
http-bio-127.0.0.1-8091-exec  0      10      0
http-bio-127.0.0.1-8092-exec  22      24      91.00
http-bio-127.0.0.1-8093-exec  0      3      0
http-nio-127.0.0.1-8084-exec  0      10      0
MIServerWorker  0      30      0


(the above is just two iterations worth for illustration)

When you see a thread pool that is at 100% utilization, it means that
when that thread dump was taken, there were no threads available to
pick up requests off the network.  Obviously, if you see the same
thread pool at 100% for multiple successive iterations, it means that
thread pool is basically saturated and the threads in them may well be
stalled on something.  See SET-21565 for an example of that.

========================

grepthread: This is a utility that will show threads in a thread dump
that match the Python regular expression you give it.  Example:

    grepthread -n 1 'locked <0x00007fd022afc1a8>' tomcat-catalina.out


The above will find all of the threads that match the above, yielding,
e.g.,:

"http-bio-127.0.0.1-8081-exec-25694" #647039 daemon prio=5 os_prio=0 tid=0x00007fcd38065000 nid=0xbfaa runnable [0x00007fcbd1414000]
   java.lang.Thread.State: RUNNABLE
	at org.bouncycastle.crypto.internal.digests.GeneralDigest.finish(Unknown Source)
	at org.bouncycastle.crypto.fips.SHA256Digest.doFinal(Unknown Source)
	at org.bouncycastle.crypto.fips.FipsSHS$LocalFipsOutputDigestCalculator.getDigest(Unknown Source)
	at org.bouncycastle.crypto.fips.FipsOutputDigestCalculator.getDigest(Unknown Source)
	at org.bouncycastle.jcajce.provider.BaseMessageDigest.engineDigest(Unknown Source)
	at java.security.MessageDigest.digest(MessageDigest.java:365)
	at com.mi.middleware.security.Sha256Crypt.Sha256_crypt(Sha256Crypt.java:278)
	at com.mi.middleware.security.Sha256Crypt.verifyPassword(Sha256Crypt.java:338)
	at com.mi.middleware.security.EncryptionUtils.validatePasswordHashInBytes(EncryptionUtils.java:289)
	- locked <0x00007fd022afc1a8> (a java.lang.Class for com.mi.middleware.security.EncryptionUtils)
	at com.mi.middleware.service.impl.MIUserServiceImpl.authenticateUserByPrincipalOrEmail(MIUserServiceImpl.java:2620)
	at com.mi.middleware.service.impl.MIUserServiceImpl.authenticateUserByPrincipalOrEmail(MIUserServiceImpl.java:2590)
	at com.mi.middleware.service.impl.MIUserServiceImpl.authenticateUserByPrincipalOrEmail(MIUserServiceImpl.java:2585)
	at com.mi.middleware.service.impl.MIUserServiceImpl$$FastClassBySpringCGLIB$$6491b4d0.invoke(<generated>)
	at org.springframework.cglib.proxy.MethodProxy.invoke(MethodProxy.java:218)
	at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.invokeJoinpoint(CglibAopProxy.java:769)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163)
	at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.proceed(CglibAopProxy.java:747)
	at org.springframework.aop.interceptor.ExposeInvocationInterceptor.invoke(ExposeInvocationInterceptor.java:93)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:186)
	at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.proceed(CglibAopProxy.java:747)
	at org.springframework.aop.framework.CglibAopProxy$DynamicAdvisedInterceptor.intercept(CglibAopProxy.java:689)
	at com.mi.middleware.service.impl.MIUserServiceImpl$$EnhancerBySpringCGLIB$$50a4fd80.authenticateUserByPrincipalOrEmail(<generated>)
	at sun.reflect.GeneratedMethodAccessor690.invoke(Unknown Source)
	at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.lang.reflect.Method.invoke(Method.java:498)
	at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:344)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.invokeJoinpoint(ReflectiveMethodInvocation.java:198)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163)
	at org.springframework.orm.hibernate5.support.OpenSessionInterceptor.invoke(OpenSessionInterceptor.java:99)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:186)
	at com.mi.middleware.interceptor.MITransactionInterceptor.invoke(MITransactionInterceptor.java:109)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:186)
	at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:212)
	at com.sun.proxy.$Proxy193.authenticateUserByPrincipalOrEmail(Unknown Source)
	at com.mi.security.MIAuthenticationProvider.retrieveUser(MIAuthenticationProvider.java:209)
	at org.springframework.security.authentication.dao.AbstractUserDetailsAuthenticationProvider.authenticate(AbstractUserDetailsAuthenticationProvider.java:144)
	at org.springframework.security.authentication.ProviderManager.authenticate(ProviderManager.java:175)
	at org.springframework.security.authentication.ProviderManager.authenticate(ProviderManager.java:200)
	at org.springframework.security.web.authentication.www.BasicAuthenticationFilter.doFilterInternal(BasicAuthenticationFilter.java:180)
	at org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:119)
	at org.springframework.security.web.FilterChainProxy$VirtualFilterChain.doFilter(FilterChainProxy.java:334)
	at org.springframework.security.web.header.HeaderWriterFilter.doFilterInternal(HeaderWriterFilter.java:74)
	at org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:119)
	at org.springframework.security.web.FilterChainProxy$VirtualFilterChain.doFilter(FilterChainProxy.java:334)
	at org.springframework.security.web.context.request.async.WebAsyncManagerIntegrationFilter.doFilterInternal(WebAsyncManagerIntegrationFilter.java:56)
	at org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:119)
	at org.springframework.security.web.FilterChainProxy$VirtualFilterChain.doFilter(FilterChainProxy.java:334)
	at org.springframework.security.web.context.SecurityContextPersistenceFilter.doFilter(SecurityContextPersistenceFilter.java:105)
	at org.springframework.security.web.FilterChainProxy$VirtualFilterChain.doFilter(FilterChainProxy.java:334)
	at org.springframework.security.web.FilterChainProxy.doFilterInternal(FilterChainProxy.java:215)
	at org.springframework.security.web.FilterChainProxy.doFilter(FilterChainProxy.java:178)
	at org.springframework.web.filter.DelegatingFilterProxy.invokeDelegate(DelegatingFilterProxy.java:358)
	at org.springframework.web.filter.DelegatingFilterProxy.doFilter(DelegatingFilterProxy.java:271)
	at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
	at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
	at com.mi.spring.filters.HTTP401ServletFilter.doFilter(HTTP401ServletFilter.java:41)
	at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
	at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
	at org.tuckey.web.filters.urlrewrite.RuleChain.handleRewrite(RuleChain.java:164)
	at org.tuckey.web.filters.urlrewrite.RuleChain.doRules(RuleChain.java:141)
	at org.tuckey.web.filters.urlrewrite.UrlRewriter.processRequest(UrlRewriter.java:90)
	at org.tuckey.web.filters.urlrewrite.UrlRewriteFilter.doFilter(UrlRewriteFilter.java:417)
	at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
	at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
	at com.mi.filter.CacheFilter.doFilter(CacheFilter.java:94)
	at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
	at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
	at org.apache.catalina.core.StandardWrapperValve.invoke(StandardWrapperValve.java:219)
	at org.apache.catalina.core.StandardContextValve.invoke(StandardContextValve.java:110)
	at org.apache.catalina.authenticator.AuthenticatorBase.invoke(AuthenticatorBase.java:492)
	at org.apache.catalina.core.StandardHostValve.invoke(StandardHostValve.java:165)
	at org.apache.catalina.valves.ErrorReportValve.invoke(ErrorReportValve.java:104)
	at com.mobileiron.catalina.valves.MobileIronAccessLogValve.invoke(MobileIronAccessLogValve.java:218)
	at org.apache.catalina.core.StandardEngineValve.invoke(StandardEngineValve.java:116)
	at org.apache.catalina.connector.CoyoteAdapter.service(CoyoteAdapter.java:452)
	at org.apache.coyote.http11.AbstractHttp11Processor.process(AbstractHttp11Processor.java:1201)
	at org.apache.coyote.AbstractProtocol$AbstractConnectionHandler.process(AbstractProtocol.java:654)
	at org.apache.tomcat.util.net.JIoEndpoint$SocketProcessor.run(JIoEndpoint.java:319)
	- locked <0x00007fdf94c0efe0> (a org.apache.tomcat.util.net.SocketWrapper)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at org.apache.tomcat.util.threads.TaskThread$WrappingRunnable.run(TaskThread.java:61)
	at java.lang.Thread.run(Thread.java:748)


Now, note the use of "-n 1" in the example command.  This limits the
output to one match, which is what the above is.



An example of a perhaps more advanced usage of "grepthread" might be
from analying this, from SET-19268 (the monitor run is contained in
"new_logs.zip" which is attached to that ticket):

kevin@kevin-ubuntu-vm-1:/tmp/set19268/2020-01-28-16-54-05$ threadpool-usage.sh tomcat-catalina.out | grep '100.00$' | sort | uniq -c | sort -nr
     60 http-bio-127.0.0.1-8083-exec  60      60      100.00
      1 http-bio-127.0.0.1-8092-exec  24      24      100.00
      1 http-bio-127.0.0.1-8092-exec  16      16      100.00
      1 http-bio-127.0.0.1-8092-exec  14      14      100.00
      1 http-bio-127.0.0.1-8092-exec  12      12      100.00
kevin@kevin-ubuntu-vm-1:/tmp/set19268/2020-01-28-16-54-05$ 


In the above, you can see that we have 60 instances of a 100% full
thread pool in http-bio-127.0.0.1-8083-exec.  It turns out that this
is the number of iterations in the monitor run.  We can see what the
most common things the threads are doing are:

kevin@kevin-ubuntu-vm-1:/tmp/set19268/2020-01-28-16-54-05$ grepthread http-bio-127.0.0.1-8083-exec tomcat-catalina.out | grep 'at ' | filterthreads | sort | uniq -c | sort -nr | head
   3555         at java.net.SocketInputStream.socketRead(SocketInputStream.java:116)
   3555         at java.net.SocketInputStream.socketRead0(Native Method)
   3555         at java.net.SocketInputStream.read(SocketInputStream.java:171)
   3555         at java.net.SocketInputStream.read(SocketInputStream.java:141)
   2715         at com.mobileiron.catalina.valves.MobileIronAccessLogValve.invoke(MobileIronAccessLogValve.java:218)
   2715         at com.mi.spring.filters.HTTP401ServletFilter.doFilter(HTTP401ServletFilter.java:41)
   2715         at com.mi.filter.CacheFilter.doFilter(CacheFilter.java:94)
   2713         at com.mi.apple.mdm.controller.MDMController.handleRequestInternal(MDMController.java:77)
   2668         at com.mi.apple.mdm.controller.MDMUtils.getHttpRequestPayload(MDMUtils.java:88)
   2668         at com.mi.apple.mdm.controller.MDMController.handleRequestInternal2(MDMController.java:140)


Now, even after using "filterthreads" (described below), the above
still shows some boilerplate stuff, but it's much easier to pick out
the fruit.  In this case, that would be:

   2668         at com.mi.apple.mdm.controller.MDMUtils.getHttpRequestPayload(MDMUtils.java:88)

Here, it's retrieving the request payload.  Nearly *every* instance is
doing this.  In that SET ticket, we used that to conclude that devices
were just sitting there and being slow to send their request payloads.

And note, too, that even more common in the above is the call to
socketRead0, which says that the threads are waiting for data from the
network.

And if we want to see if there's any common class method invocation
that matters for the threads that have the above method call, we can
do this:

kevin@kevin-ubuntu-vm-1:/tmp/set19268/2020-01-28-16-54-05$ grepthread http-bio-127.0.0.1-8083-exec tomcat-catalina.out | grepthread 'at com.mi.apple.mdm.controller.MDMUtils.getHttpRequestPayload' | grep 'at ' | filterthreads | sort | uniq -c | sort -nr | head
   2668         at java.net.SocketInputStream.socketRead(SocketInputStream.java:116)
   2668         at java.net.SocketInputStream.socketRead0(Native Method)
   2668         at java.net.SocketInputStream.read(SocketInputStream.java:171)
   2668         at java.net.SocketInputStream.read(SocketInputStream.java:141)
   2668         at com.mobileiron.catalina.valves.MobileIronAccessLogValve.invoke(MobileIronAccessLogValve.java:218)
   2668         at com.mi.spring.filters.HTTP401ServletFilter.doFilter(HTTP401ServletFilter.java:41)
   2668         at com.mi.filter.CacheFilter.doFilter(CacheFilter.java:94)
   2668         at com.mi.apple.mdm.controller.MDMUtils.getHttpRequestPayload(MDMUtils.java:88)
   2668         at com.mi.apple.mdm.controller.MDMController.handleRequestInternal(MDMController.java:77)
   2668         at com.mi.apple.mdm.controller.MDMController.handleRequestInternal2(MDMController.java:140)

This confirms that *every* thread that's getting the request payload
is waiting on the network.



If you give no arguments to "grepthread", it will show an extensive
usage description, which includes all of the options that can be
passed to it.  "grepthread" just makes use of grepblocks.py, a Python
program that does the heavy lifting.  You can use grepblocks.py
directly, but it is coded to use a default block pattern (the pattern
it uses to distinguish between text sections) that matches Tomcat log
messages (like what you find in mifs.log).

Python regular expressions are documented here:
https://docs.python.org/2/library/re.html#regular-expression-syntax

There are a number of tutorials online about regular expressions, such
as https://www.regular-expressions.info/tutorial.html


===============================

filterthreads: This will filter out a lot of the boilerplate junk that
litters our stack traces, leaving mostly more useful and meaningful
things.  For instance, it'll turn this:

"http-bio-127.0.0.1-8083-exec-60" #591 daemon prio=5 os_prio=0 tid=0x00007f5148023800 nid=0x3d5e runnable [0x00007f4edc18a000]
   java.lang.Thread.State: RUNNABLE
   at java.net.SocketInputStream.socketRead0(Native Method)
   at java.net.SocketInputStream.socketRead(SocketInputStream.java:116)
   at java.net.SocketInputStream.read(SocketInputStream.java:171)
   at java.net.SocketInputStream.read(SocketInputStream.java:141)
   at org.apache.coyote.http11.InternalInputBuffer.fill(InternalInputBuffer.java:550)
   at org.apache.coyote.http11.InternalInputBuffer.fill(InternalInputBuffer.java:519)
   at org.apache.coyote.http11.InternalInputBuffer$InputStreamInputBuffer.doRead(InternalInputBuffer.java:581)
   at org.apache.coyote.http11.filters.IdentityInputFilter.doRead(IdentityInputFilter.java:137)
   at org.apache.coyote.http11.AbstractInputBuffer.doRead(AbstractInputBuffer.java:293)
   at org.apache.coyote.Request.doRead(Request.java:438)
   at org.apache.catalina.connector.InputBuffer.realReadBytes(InputBuffer.java:290)
   at org.apache.tomcat.util.buf.ByteChunk.checkEof(ByteChunk.java:422)
   at org.apache.tomcat.util.buf.ByteChunk.substract(ByteChunk.java:404)
   at org.apache.catalina.connector.InputBuffer.read(InputBuffer.java:315)
   at org.apache.catalina.connector.CoyoteInputStream.read(CoyoteInputStream.java:200)
   at com.mi.apple.mdm.controller.MDMUtils.getHttpRequestPayload(MDMUtils.java:88)
   at com.mi.apple.mdm.controller.MDMController.handleRequestInternal2(MDMController.java:140)
   at com.mi.apple.mdm.controller.MDMController.handleRequestInternal(MDMController.java:77)
   at org.springframework.web.servlet.mvc.AbstractController.handleRequest(AbstractController.java:177)
   at org.springframework.web.servlet.mvc.SimpleControllerHandlerAdapter.handle(SimpleControllerHandlerAdapter.java:52)
   at org.springframework.web.servlet.DispatcherServlet.doDispatch(DispatcherServlet.java:1039)
   at org.springframework.web.servlet.DispatcherServlet.doService(DispatcherServlet.java:942)
   at org.springframework.web.servlet.FrameworkServlet.processRequest(FrameworkServlet.java:1005)
   at org.springframework.web.servlet.FrameworkServlet.doPut(FrameworkServlet.java:919)
   at javax.servlet.http.HttpServlet.service(HttpServlet.java:653)
   at org.springframework.web.servlet.FrameworkServlet.service(FrameworkServlet.java:882)
   at javax.servlet.http.HttpServlet.service(HttpServlet.java:731)
   at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:303)
   at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
   at org.apache.tomcat.websocket.server.WsFilter.doFilter(WsFilter.java:52)
   at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
   at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
   at org.togglz.servlet.TogglzFilter.doFilter(TogglzFilter.java:100)
   at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
   at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
   at org.springframework.security.web.FilterChainProxy.doFilterInternal(FilterChainProxy.java:209)
   at org.springframework.security.web.FilterChainProxy.doFilter(FilterChainProxy.java:178)
   at org.springframework.web.filter.DelegatingFilterProxy.invokeDelegate(DelegatingFilterProxy.java:357)
   at org.springframework.web.filter.DelegatingFilterProxy.doFilter(DelegatingFilterProxy.java:270)
   at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
   at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
   at com.mi.spring.filters.HTTP401ServletFilter.doFilter(HTTP401ServletFilter.java:41)
   at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
   at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
   at org.tuckey.web.filters.urlrewrite.RuleChain.handleRewrite(RuleChain.java:164)
   at org.tuckey.web.filters.urlrewrite.RuleChain.doRules(RuleChain.java:141)
   at org.tuckey.web.filters.urlrewrite.UrlRewriter.processRequest(UrlRewriter.java:90)
   at org.tuckey.web.filters.urlrewrite.UrlRewriteFilter.doFilter(UrlRewriteFilter.java:417)
   at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
   at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
   at com.mi.filter.CacheFilter.doFilter(CacheFilter.java:94)
   at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:241)
   at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:208)
   at org.apache.catalina.core.StandardWrapperValve.invoke(StandardWrapperValve.java:219)
   at org.apache.catalina.core.StandardContextValve.invoke(StandardContextValve.java:110)
   at org.apache.catalina.authenticator.AuthenticatorBase.invoke(AuthenticatorBase.java:494)
   at org.apache.catalina.core.StandardHostValve.invoke(StandardHostValve.java:169)
   at org.apache.catalina.valves.ErrorReportValve.invoke(ErrorReportValve.java:104)
   at com.mobileiron.catalina.valves.MobileIronAccessLogValve.invoke(MobileIronAccessLogValve.java:218)
   at org.apache.catalina.core.StandardEngineValve.invoke(StandardEngineValve.java:116)
   at org.apache.catalina.connector.CoyoteAdapter.service(CoyoteAdapter.java:445)
   at org.apache.coyote.http11.AbstractHttp11Processor.process(AbstractHttp11Processor.java:1137)
   at org.apache.coyote.AbstractProtocol$AbstractConnectionHandler.process(AbstractProtocol.java:637)
   at org.apache.tomcat.util.net.JIoEndpoint$SocketProcessor.run(JIoEndpoint.java:316)
   - locked <0x00007f5477119978> (a org.apache.tomcat.util.net.SocketWrapper)
   at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
   at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
   at org.apache.tomcat.util.threads.TaskThread$WrappingRunnable.run(TaskThread.java:61)
   at java.lang.Thread.run(Thread.java:748)


into this:

"http-bio-127.0.0.1-8083-exec-60" #591 daemon prio=5 os_prio=0 tid=0x00007f5148023800 nid=0x3d5e runnable [0x00007f4edc18a000]
   java.lang.Thread.State: RUNNABLE
   at java.net.SocketInputStream.socketRead0(Native Method)
   at java.net.SocketInputStream.socketRead(SocketInputStream.java:116)
   at java.net.SocketInputStream.read(SocketInputStream.java:171)
   at java.net.SocketInputStream.read(SocketInputStream.java:141)
   at com.mi.apple.mdm.controller.MDMUtils.getHttpRequestPayload(MDMUtils.java:88)
   at com.mi.apple.mdm.controller.MDMController.handleRequestInternal2(MDMController.java:140)
   at com.mi.apple.mdm.controller.MDMController.handleRequestInternal(MDMController.java:77)
   at com.mi.spring.filters.HTTP401ServletFilter.doFilter(HTTP401ServletFilter.java:41)
   at com.mi.filter.CacheFilter.doFilter(CacheFilter.java:94)
   at com.mobileiron.catalina.valves.MobileIronAccessLogValve.invoke(MobileIronAccessLogValve.java:218)



===============================

cpu-usage: This utility takes zero or more files (when zero, it reads
from stdin) like monitor-threads-<date>.log and shows the
process/thread IDs, average CPU usage, and command for each.  It shows
the process/thread ID in both decimal and hexadecimal (the latter
making it easy to search thread dumps for threads with that ID).

Example:

kevin@kevin-ubuntu-vm-1:/tmp/set21923/2021-08-10-23-07-47$ cpu-usage monitor-threads-2021-08-10-23.log | head
95199     0x173df  76.29  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=tmobile.mobileiron.net-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/def+
95194     0x173da  14.46  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=tmobile.mobileiron.net-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/def+
95196     0x173dc  14.31  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=tmobile.mobileiron.net-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/def+
95197     0x173dd  14.15  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=tmobile.mobileiron.net-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/def+
95193     0x173d9  14.15  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=tmobile.mobileiron.net-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/def+
95192     0x173d8  13.99  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=tmobile.mobileiron.net-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/def+
95195     0x173db  13.67  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=tmobile.mobileiron.net-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/def+
119506    0x1d2d2  5.77  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql
95198     0x173de  5.54  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=tmobile.mobileiron.net-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/def+
76439     0x12a97  3.33  grep-F[GC(AllocationFailure)/var/log/tomcat/gc.log

And let's say you want to find out what thread 95199 (the thread in
the above that used the most overall CPU) is in the thread dump.  Then
using the second column value from the first row of the output above,
you'd do:

    grepthread -n 1 'nid=0x173df' tomcat-catalina.out

where you use "-n 1" in the above to limit yourself to the first matching thread stack output.  In this case, though, you get:

"VM Thread" os_prio=0 tid=0x00007fe0201b1800 nid=0x173df runnable


Which isn't all that interesting (except it tells you that the JVM was
spending most of its time doing garbage collection).


But let's look at another example:

kevin@kevin-ubuntu-vm-1:/tmp/set19268/2020-01-27-11-00-04$ cpu-usage monitor-threads-2020-01-27-11.log | head
3229      0xc9d  16.23  /usr/java/default/bin/java-Djava.util.logging.config.file=/mi/tomcat/conf/logging.properties-Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager-Xbootclasspath/p:/mi/tomcat/lib/alpn-boot-8.1.14-VSP-SNAPSHOT.jar-Xms128m-Xmx2048m-XX:PermSize=512m-XX:MaxPermSize=512m-XX:+OptimizeStringConcat-server-Dvsp.branding=mobileiron-Dmi.hostname=emm-core01.f-i.de-Dfile.encoding=utf-8-Djavax.net.ssl.keyStore=/usr/java/default/j+
4368      0x1110  13.65  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql
10912     0x2aa0  13.18  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql
19114     0x4aaa  12.81  sshd:misupport@notty
24171     0x5e6b  11.83  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql
13299     0x33f3  11.47  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql
13304     0x33f8  11.44  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql
4363      0x110b  11.27  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql
13303     0x33f7  10.78  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql
17957     0x4625  10.61  /usr/sbin/mysqld--datadir=/mi/files/mysql--socket=/var/lib/mysql/mysql.sock--pid-file=/var/run/mobileiron-core-mysqld/mobileiron-core-mysqld.pid--basedir=/usr--user=mysql


Here we can see that the topmost CPU using process is tomcat, but the
ones following it are MySQL.  MySQL thread IDs won't appear in any
thread dump, of course, but it shows that having the command makes it
clear what the process/thread ID is associated with.  Let's look for
the Tomcat thread, 0xc9d, in this monitor run's catalina.out:

kevin@kevin-ubuntu-vm-1:/tmp/set19268/2020-01-27-11-00-04$ grepthread -n 1 0xc9d tomcat-catalina.out
"MIReportScheduler_Worker-5" #50 prio=4 os_prio=0 tid=0x00007eff9b27c800 nid=0xc9d in Object.wait() [0x00007eff812ef000]
   java.lang.Thread.State: TIMED_WAITING (on object monitor)
	at java.lang.Object.wait(Native Method)
	at com.mi.ecm.AbstractService.postAndWait(AbstractService.java:187)
	- locked <0x00007f0066e6b578> (a com.mi.ec.protocol.v1.WorkOrder)
	at com.mi.ecm.SystemService.testConnector(SystemService.java:263)
	at com.mi.ecm.ConnectorService.testConnector(ConnectorService.java:1550)
	at com.mi.ecm.ConnectorService$$FastClassBySpringCGLIB$$e9681dec.invoke(<generated>)
	at org.springframework.cglib.proxy.MethodProxy.invoke(MethodProxy.java:218)
	at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.invokeJoinpoint(CglibAopProxy.java:749)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163)
	at org.springframework.transaction.interceptor.TransactionInterceptor$$Lambda$137/1833314908.proceedWithInvocation(Unknown Source)
	at org.springframework.transaction.interceptor.TransactionAspectSupport.invokeWithinTransaction(TransactionAspectSupport.java:295)
	at org.springframework.transaction.interceptor.TransactionInterceptor.invoke(TransactionInterceptor.java:98)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:186)
	at org.springframework.aop.framework.CglibAopProxy$DynamicAdvisedInterceptor.intercept(CglibAopProxy.java:688)
	at com.mi.ecm.ConnectorService$$EnhancerBySpringCGLIB$$49b99003.testConnector(<generated>)
	at com.mi.middleware.service.impl.diagnostic.ConnectorDiagnostic.testConnector(ConnectorDiagnostic.java:63)
	at com.mi.middleware.service.impl.diagnostic.ConnectorDiagnostic.runDiagnostic(ConnectorDiagnostic.java:36)
	at com.mi.middleware.service.impl.ServiceDiagnosticImpl.runDiagnostic(ServiceDiagnosticImpl.java:227)
	at com.mi.middleware.service.impl.ServiceDiagnosticImpl.testAll(ServiceDiagnosticImpl.java:170)
	at com.mi.middleware.service.ServiceDiagnosticJobQuartz.execute(ServiceDiagnosticJobQuartz.java:25)
	at org.quartz.core.JobRunShell.run(JobRunShell.java:202)
	at org.quartz.simpl.SimpleThreadPool$WorkerThread.run(SimpleThreadPool.java:573)
	- locked <0x00007f0072904bb8> (a java.lang.Object)


Here the thread that was eating the most overall CPU was the report
scheduler worker.  Again note the use of "-n 1" in the command, to
limit the output to one matching thread instance.



Feel free to email me with any questions.


-- Kevin Brown (kevin.brown@ivanti.com), 2021-09-15
