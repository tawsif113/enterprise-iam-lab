package com.example.ticketapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;

@SpringBootApplication
@EnableMethodSecurity
public class TicketApiApplication {
    public static void main(String[] args) {
        SpringApplication.run(TicketApiApplication.class, args);
    }
}
