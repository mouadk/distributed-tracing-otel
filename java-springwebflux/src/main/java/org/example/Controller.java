package org.example;

import org.springframework.http.HttpHeaders;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.reactive.ReactiveKafkaProducerTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
public class Controller {

    @Autowired
    private ReactiveKafkaProducerTemplate<String, String> kafkaTemplate;

    @PostMapping("/publish")
    public Mono<String> sendMessage(@RequestBody String message, @RequestHeader HttpHeaders headers) {
        return Mono.just(headers)
                .doOnNext(h -> System.out.println("Received headers: " + h))
                .then(kafkaTemplate.send("test-topic", message))
                .doOnError(throwable -> System.out.println("Error occurred while publishing message: " + throwable.getMessage()))
                .then(Mono.just("Message published"));
    }
}