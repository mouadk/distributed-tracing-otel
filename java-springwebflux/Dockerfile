FROM maven:3.9.8-eclipse-temurin-17 AS builder
WORKDIR /app
COPY /src ./src
COPY pom.xml ./pom.xml
RUN mvn clean package

FROM amazoncorretto:17
COPY --from=builder /app/target/java-springwebflux-1.0.0-SNAPSHOT.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]
