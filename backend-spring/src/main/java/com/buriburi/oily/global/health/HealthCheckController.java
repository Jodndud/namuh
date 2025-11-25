package com.buriburi.oily.global.health;

import io.swagger.v3.oas.annotations.Hidden;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import static org.springframework.http.HttpStatus.OK;

@Hidden
@RestController
@Tag(name = "Health-Check")
public class HealthCheckController {

    @GetMapping("/health-check")
    public ResponseEntity<Void> checkHealthStatus() {

        return new ResponseEntity<>(OK);
    }

}