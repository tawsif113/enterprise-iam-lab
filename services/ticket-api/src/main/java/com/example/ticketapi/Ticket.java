package com.example.ticketapi;

public record Ticket(
    String id,
    String title,
    String priority,
    String status,
    String department,
    String assignedTo
) {
}
