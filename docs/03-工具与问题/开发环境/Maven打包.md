# Maven构建Jar包

## pom.xml需要添加以下配置

```java
 <build>
        <resources>
            <resource>
                <directory>src/main/resources</directory>
                <includes>
                    <include>**/*.exe</include> <!-- 明确包含 .exe 文件 -->
                </includes>
                <filtering>false</filtering> <!-- 禁止过滤二进制文件 -->
            </resource>
        </resources>
        <plugins>
            <!-- 打包可执行 JAR -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.5.0</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <!-- 指定主类 -->
                            <transformers>
                                <transformer
                               implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>填写主类</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
```