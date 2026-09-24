package com.example.ticketapi;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Service;

@Service
public class TicketService {

    private final List<Ticket> tickets = List.of(
        new Ticket("TKT-1001", "Unable to access payroll portal", "HIGH", "OPEN", "HR", "alice"),
        new Ticket("TKT-1002", "VPN connection failing", "CRITICAL", "IN_PROGRESS", "IT", "bob"),
        new Ticket("TKT-1003", "Email account locked", "MEDIUM", "OPEN", "Operations", null),
        new Ticket("TKT-1004", "Laptop encryption warning", "HIGH", "OPEN", "Security", "alice"),
        new Ticket("TKT-1005", "New employee account request", "LOW", "RESOLVED", "HR", "bob"),
        new Ticket("TKT-1006", "CRM dashboard unavailable", "CRITICAL", "OPEN", "Sales", null),
        new Ticket("TKT-1007", "Printer access request", "LOW", "IN_PROGRESS", "Finance", "alice"),
        new Ticket("TKT-1008", "Suspicious login alert", "HIGH", "RESOLVED", "Security", "bob")
    );

    public List<Ticket> all() {
        return tickets;
    }

    public Ticket byId(String id) {
        return tickets.stream()
            .filter(ticket -> ticket.id().equalsIgnoreCase(id))
            .findFirst()
            .orElse(null);
    }

    public List<Ticket> supportQueue() {
        return tickets.stream()
            .filter(ticket -> !"RESOLVED".equals(ticket.status()))
            .toList();
    }

    public Map<String, Object> metrics() {
        long open = tickets.stream().filter(ticket -> "OPEN".equals(ticket.status())).count();
        long inProgress = tickets.stream().filter(ticket -> "IN_PROGRESS".equals(ticket.status())).count();
        long resolved = tickets.stream().filter(ticket -> "RESOLVED".equals(ticket.status())).count();
        long critical = tickets.stream().filter(ticket -> "CRITICAL".equals(ticket.priority())).count();

        return Map.of(
            "total", tickets.size(),
            "open", open,
            "inProgress", inProgress,
            "resolved", resolved,
            "critical", critical
        );
    }
}
