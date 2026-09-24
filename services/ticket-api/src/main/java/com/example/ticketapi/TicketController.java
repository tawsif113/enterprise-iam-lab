package com.example.ticketapi;

import java.util.Map;

import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TicketController {

    @GetMapping("/public")
    Map<String, Object> publicEndpoint() {
        return Map.of("status", "ok", "message", "No token required");
    }

    @GetMapping("/api/me")
    Map<String, Object> me(@AuthenticationPrincipal Jwt jwt) {
        return Map.of(
            "sub", jwt.getSubject(),
            "issuer", jwt.getIssuer().toString(),
            "audience", jwt.getAudience(),
            "username", jwt.getClaimAsString("preferred_username"),
            "email", jwt.getClaimAsString("email")
        );
    }

    @GetMapping("/api/tickets")
    Map<String, Object> tickets(@AuthenticationPrincipal Jwt jwt) {
        return Map.of(
            "message", "Authenticated access to ticket data",
            "subject", jwt.getSubject()
        );
    }

    @PreAuthorize("hasRole('SUPPORT_AGENT')")
    @GetMapping("/api/support")
    Map<String, Object> support() {
        return Map.of("message", "support-agent role accepted");
    }
}
