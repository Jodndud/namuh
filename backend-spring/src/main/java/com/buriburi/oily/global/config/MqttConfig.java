package com.buriburi.oily.global.config;

import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.MqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.integration.channel.DirectChannel;
import org.springframework.integration.channel.PublishSubscribeChannel;
import org.springframework.integration.core.MessageProducer;
import org.springframework.integration.mqtt.core.DefaultMqttPahoClientFactory;
import org.springframework.integration.mqtt.core.MqttPahoClientFactory;
import org.springframework.integration.mqtt.inbound.MqttPahoMessageDrivenChannelAdapter;
import org.springframework.integration.mqtt.outbound.MqttPahoMessageHandler;
import org.springframework.integration.mqtt.support.DefaultPahoMessageConverter;
import org.springframework.integration.mqtt.support.MqttHeaders;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.MessageHandler;

import javax.net.ssl.SSLSocketFactory;

@Slf4j
@Configuration
public class MqttConfig {

    private static final String MQTT_CLIENT_ID = MqttAsyncClient.generateClientId(); // 클라이언트 고유식볋자

    @Value("${spring.mqtt.broker-url}")
    private String BROKER_URL; // 브로커 주소

    @Value("${spring.mqtt.topic}")
    private String DEFAULT_TOPIC; // Topic

    @Value("${spring.mqtt.username}")
    private String MQTT_USERNAME;

    @Value("${spring.mqtt.password}")
    private String MQTT_PASSWORD;

    /**
     * MQTT 연결 옵션 설정
     */
    @Bean
    public MqttConnectOptions mqttConnectOptions() {
        MqttConnectOptions options = new MqttConnectOptions();
        options.setServerURIs(new String[]{BROKER_URL});
        options.setUserName(MQTT_USERNAME);
        options.setPassword(MQTT_PASSWORD.toCharArray());

        options.setSocketFactory(SSLSocketFactory.getDefault());

        options.setCleanSession(true);
        options.setAutomaticReconnect(true);
        options.setConnectionTimeout(10);
        return options;
    }

    /**
     * 연결 옵션을 사용하는 MQTT 클라이언트 팩토리
     */
    @Bean
    public MqttPahoClientFactory mqttClientFactory() {
        DefaultMqttPahoClientFactory factory = new DefaultMqttPahoClientFactory();
        factory.setConnectionOptions(mqttConnectOptions());
        return factory;
    }

    // --- Inbound (Mqtt -> Spring 메시지 수신)

    @Bean
    public MessageChannel mqttInputChannel() {
        // Point to Point Channel 중 가장 기본
        // messageHandler에게 Message를 전송
        // DirectChannel을 구독하는 핸들러 하나에게만 브로드 캐스트
        // return new DirectChannel();

        // PublishSubscribeChannel은 Publish/Subscribe Channel로
        // 해당 채널을 구독한 모든 핸들러에게 브로드 캐스트
        return new PublishSubscribeChannel();
    }

    @Bean
    public MessageProducer inbound() {
        // 메시지 수신을 위한 채널을 구성
        // 생성자를 통해 topic을 여러개 추가할 수 있음.
        // addTopic() 메서드도 존재함.
        // 생성자 대신 MqttPahoClientFactory를 사용하도록 수정
        MqttPahoMessageDrivenChannelAdapter adapter =
                new MqttPahoMessageDrivenChannelAdapter(MQTT_CLIENT_ID + "-inbound", mqttClientFactory(), DEFAULT_TOPIC);

        adapter.setCompletionTimeout(5000); // 메시지 처리가 5초를 초과하면 타임아웃으로 간주
        adapter.setConverter(new DefaultPahoMessageConverter()); // MQTT 메시지를 Spring Integration 메시지로 변환
        adapter.setQos(1);  // Qos 설정
        adapter.setOutputChannel(mqttInputChannel()); // Spring Integration 채널 설정
        return adapter;
    }

    // --- Outbound (Spring -> MQTT: 메시지 발행) ---
    @Bean(name = "mqttOutboundChannel")
    public MessageChannel mqttOutputChannel() {
        return new DirectChannel();
    }

    @Bean
    @ServiceActivator(inputChannel = "mqttOutboundChannel")
    public MessageHandler mqttOutboundHandler() {
        // 발행(Publish)를 위한 핸들러
        MqttPahoMessageHandler messageHandler =
                new MqttPahoMessageHandler(MQTT_CLIENT_ID + "-outbound", mqttClientFactory());
        messageHandler.setAsync(true);
        messageHandler.setDefaultTopic(DEFAULT_TOPIC);
        return messageHandler;
    }
}