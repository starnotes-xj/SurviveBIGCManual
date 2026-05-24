## Lombok在maven编译运行时找不到符号解决方案

在构建中加入如下内容即可

构建：

```xml
<build>
<plugins> 
    <!--            在这里添加下面的maven编译插件-->
    </plugins>
</build>
```

需要加入的内容：

```xml
<plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
```

