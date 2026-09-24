package com.example.ticketapi;

import java.util.Collection;
import java.util.List;
import java.util.Map;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public").permitAll()
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth -> oauth
                .jwt(jwt -> jwt.jwtAuthenticationConverter(keycloakConverter())))
            .build();
    }

    private Converter<Jwt, ? extends AbstractAuthenticationToken> keycloakConverter() {
        return jwt -> {
            Object rawRealmAccess = jwt.getClaims().get("realm_access");
            Collection<GrantedAuthority> authorities = List.of();

            if (rawRealmAccess instanceof Map<?, ?> realmAccess) {
                Object rawRoles = realmAccess.get("roles");
                if (rawRoles instanceof Collection<?> roles) {
                    authorities = roles.stream()
                        .map(Object::toString)
                        .map(role -> new SimpleGrantedAuthority("ROLE_" + role.toUpperCase().replace('-', '_')))
                        .map(GrantedAuthority.class::cast)
                        .toList();
                }
            }

            return new JwtAuthenticationToken(jwt, authorities, jwt.getSubject());
        };
    }
}
