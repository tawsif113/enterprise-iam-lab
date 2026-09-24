package com.example.ticketapi;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class TicketController {

    private final TicketService ticketService;

    public TicketController(TicketService ticketService) {
        this.ticketService = ticketService;
    }

    @GetMapping("/public")
    Map<String, Object> publicEndpoint() {
        return Map.of(
            "status", "ok",
            "message", "No token required"
        );
    }

    @GetMapping("/api/me")
    Map<String, Object> me(JwtAuthenticationToken authentication) {
        var jwt = authentication.getToken();

        Map<String, Object> identity = new LinkedHashMap<>();
        identity.put("subject", jwt.getSubject());
        identity.put("username", jwt.getClaimAsString("preferred_username"));
        identity.put("email", jwt.getClaimAsString("email"));

        Map<String, Object> token = new LinkedHashMap<>();
        token.put("issuer", jwt.getIssuer() == null ? null : jwt.getIssuer().toString());
        token.put("audience", jwt.getAudience());
        token.put("issuedAt", jwt.getIssuedAt());
        token.put("expiresAt", jwt.getExpiresAt());

        List<String> authorities = authentication.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .sorted()
            .toList();

        return Map.of(
            "identity", identity,
            "token", token,
            "authorization", Map.of("authorities", authorities)
        );
    }

    @PreAuthorize("hasRole('EMPLOYEE')")
    @GetMapping("/api/tickets")
    List<Ticket> tickets() {
        return ticketService.all();
    }

    @PreAuthorize("hasRole('EMPLOYEE')")
    @GetMapping("/api/tickets/{id}")
    Ticket ticket(@PathVariable String id) {
        Ticket ticket = ticketService.byId(id);
        if (ticket == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Ticket not found");
        }
        return ticket;
    }

    @PreAuthorize("hasRole('SUPPORT_AGENT')")
    @GetMapping("/api/support/queue")
    List<Ticket> supportQueue() {
        return ticketService.supportQueue();
    }

    @PreAuthorize("hasRole('PORTAL_ADMIN')")
    @GetMapping("/api/admin/metrics")
    Map<String, Object> metrics() {
        return ticketService.metrics();
    }
}
