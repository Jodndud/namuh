# V3 변경사항: 더 적극적인 움직임과 단순화된 Curriculum

## 최신 업데이트 (2025-11-16)

### ✅ Gripper 구조 정확도 개선

**실제 Dofbot Gripper 구조:**

- `grip_joint`: 그리퍼 움직임 담당 조인트 (1-DOF)
- `rlink2`, `llink2`: 실제로 물건을 잡는 양쪽 finger tips

**변경사항:**

1. **End-effector link 수정:**

   ```python
   # Before: ee_link_name = "arm_link5"  # 그리퍼 base
   # After:  ee_link_name = "rlink2"     # 실제 finger tip (right)
   ```

2. **Contact bodies 추가:**

   ```python
   gripper_contact_bodies = ["rlink2", "llink2"]  # 양쪽 finger tips
   ```

3. **Grasp detection 개선:**

   ```python
   # 양쪽 finger tip의 중심점 계산
   rlink2_pos = self.robot.data.body_pos_w[:, self._gripper_bodies_idx[0]]
   llink2_pos = self.robot.data.body_pos_w[:, self._gripper_bodies_idx[1]]
   gripper_center = (rlink2_pos + llink2_pos) / 2.0

   # Gripper center 기준으로 거리 계산
   d_gripper_obj = torch.linalg.norm(gripper_center - obj_pos_w, dim=-1)
   near_object = d_gripper_obj < 0.03  # 양쪽 finger tip 중심 기준
   ```

---

## 문제 상황 (V2에서 발견)

**증상:**

- ✅ REACH는 작동: 로봇 팔이 빨간색 큐브까지 다가감
- ❌ 그 이후 멈춤: 그리퍼 움직임 없음, 팔 움직임 없음
- ❌ PICK AND PLACE 실패: REACH만 되고 GRASP/LIFT로 진행 안됨

**원인 분석:**

1. **Action scale 부족**: V2는 기본 1.0x scaling → 움직임이 미미
2. **Gripper action 약함**: 5개 arm joint와 동일한 scaling → 그리퍼 강조 부족
3. **Curriculum 너무 복잡**: 5-stage → 각 stage 전환이 어려움
4. **Grasp detection 엄격**: threshold 0.1 → 너무 가까이 가야 grasp 감지
5. **Jerk penalty**: 급격한 움직임 억제 → exploration 방해

---

## V3 주요 개선사항

### 1. 📈 Aggressive Action Scaling

| Component          | V2   | V3       | 증가율 |
| ------------------ | ---- | -------- | ------ |
| **Arm Actions**    | 1.0x | **2.5x** | 150% ↑ |
| **Gripper Action** | 1.0x | **4.0x** | 300% ↑ |

**구현:**

```python
# V3: dofbot_pickplace_env_v3.py, _pre_physics_step()
arm_actions = actions[:, :5]
gripper_actions = actions[:, 5:6]

arm_scaled = arm_actions * 2.5      # 팔: 2.5배
gripper_scaled = gripper_actions * 4.0  # 그리퍼: 4배!
```

**효과:**

- 팔 움직임 2.5배 증가 → 더 빠른 도달
- 그리퍼 움직임 4배 증가 → 확실한 grasp/release

---

### 2. 🎯 Simplified 3-Stage Curriculum

**V2 (5 stages):**

```
REACH → GRASP → LIFT → TRANSPORT → PLACE
```

**V3 (3 stages):**

```
Stage 0: REACH          (EE → Object)
Stage 1: GRASP+LIFT     (Close gripper + Lift, combined!)
Stage 2: PLACE          (Transport + Release, combined!)
```

**Why?**

- V2는 stage 전환이 너무 많아서 학습 느림
- V3는 관련 동작들을 묶어서 학습 효율 증가
- GRASP와 LIFT는 연속 동작 → 하나의 stage로 통합
- TRANSPORT와 PLACE도 연속 동작 → 하나의 stage로 통합

---

### 3. 🤲 Gripper Exploration Bonus

**V3 새로운 보상:**

```python
# V3: dofbot_pickplace_env_v3.py, _get_rewards()
gripper_movement = torch.abs(grip - self._prev_gripper_pos)
reward += 2.0 * gripper_movement  # 그리퍼가 움직이면 보상!
```

**효과:**

- 그리퍼가 가만히 있으면 보상 없음
- 그리퍼가 열고 닫으면 즉시 보상
- Early stage에서 gripper exploration 촉진

---

### 4. 🔓 Relaxed Detection Thresholds

| Threshold           | V2    | V3        | 변화      |
| ------------------- | ----- | --------- | --------- |
| **Grasp Detection** | 0.10  | **0.03**  | 70% 완화  |
| **Lift Height**     | 0.10m | **0.08m** | 20% 완화  |
| **Goal Tolerance**  | 0.05m | **0.08m** | 60% 완화  |
| **Gripper Close**   | N/A   | **-0.7**  | 새로 추가 |

**효과:**

- Grasp: 3cm 이내면 grasp 감지 (V2: 10cm) → 훨씬 쉽게 grasp
- Lift: 8cm만 들어도 성공 (V2: 10cm) → 조금만 들어도 OK
- Goal: 8cm 이내면 성공 (V2: 5cm) → placement 쉬움

---

### 5. 🚫 No Jerk Penalty

**V2:**

```yaml
rew_jerk_penalty_scale: 0.01 # 급격한 움직임 억제
```

**V3:**

```yaml
rew_jerk_penalty_scale: 0.0 # 제거!
```

**Why?**

- Jerk penalty는 smooth한 움직임을 유도하지만
- Early stage exploration을 방해함
- V3는 빠르고 급격한 움직임도 허용하여 exploration 촉진

---

### 6. 💪 Stronger Actuators

| Parameter                | V2   | V3       |
| ------------------------ | ---- | -------- |
| **Arm Damping**          | 50.0 | **60.0** |
| **Arm Effort Limit**     | 50.0 | **80.0** |
| **Gripper Damping**      | 15.0 | **20.0** |
| **Gripper Effort Limit** | 30.0 | **50.0** |

**효과:**

- 더 높은 damping → 빠른 반응
- 더 높은 effort limit → 강한 힘 (grasp/lift 용이)

---

### 7. 🪶 Lighter Object

| Parameter       | V2           | V3               |
| --------------- | ------------ | ---------------- |
| **Object Mass** | 0.03kg (30g) | **0.02kg (20g)** |

**효과:**

- 더 가벼운 물체 → grasp/lift 매우 쉬움
- Early stage 성공 확률 증가

---

### 8. 🎲 Higher Exploration (PPO Config)

| Parameter              | V2    | V3       | 변화               |
| ---------------------- | ----- | -------- | ------------------ |
| **Initial Log Std**    | 0.0   | **0.5**  | 초기 exploration ↑ |
| **Min Log Std**        | -5.0  | **-3.0** | Clamping 완화      |
| **Entropy Loss Scale** | 0.005 | **0.01** | 2배 증가           |
| **Grad Norm Clip**     | 0.5   | **1.0**  | 2배 완화           |
| **Timesteps**          | 500K  | **300K** | 40% 감소 (3-stage) |

**효과:**

- 더 높은 entropy → 더 다양한 action 시도
- 더 완화된 gradient clipping → 큰 업데이트 허용
- 더 적은 timesteps → 빠른 실험 (3-stage는 5-stage보다 단순)

---

## V2 vs V3 비교표

| 항목                     | V2    | V3    | 개선       |
| ------------------------ | ----- | ----- | ---------- |
| **Arm Action Scale**     | 1.0x  | 2.5x  | 150% ↑     |
| **Gripper Action Scale** | 1.0x  | 4.0x  | 300% ↑     |
| **Curriculum Stages**    | 5     | 3     | 40% 단순화 |
| **Grasp Threshold**      | 0.10  | 0.03  | 70% 완화   |
| **Lift Threshold**       | 0.10m | 0.08m | 20% 완화   |
| **Goal Tolerance**       | 0.05m | 0.08m | 60% 완화   |
| **Gripper Exploration**  | ❌    | ✅    | 새로 추가  |
| **Jerk Penalty**         | 0.01  | 0.0   | 제거       |
| **Action Penalty**       | 0.01  | 0.001 | 90% 감소   |
| **Entropy Scale**        | 0.005 | 0.01  | 100% ↑     |
| **Total Timesteps**      | 500K  | 300K  | 40% 감소   |
| **Object Mass**          | 30g   | 20g   | 33% 감소   |

---

## 학습 방법

### 1. V3 처음부터 학습

```bash
cd rl\dofbot_isaacLab\dofbot

# V3 학습 시작
python scripts/skrl/train.py --task=Dofbot-PickPlace-Direct-v3 --algorithm=PPO --num_envs=1024 --device=cuda --headless
```

### 2. TensorBoard 모니터링

```bash
tensorboard --logdir=logs --port=6006
```

**확인 포인트:**

- `http://localhost:6006` 접속
- **Rewards**: `rewards/stage_0_reach`, `rewards/stage_1_grasp_lift`, `rewards/stage_2_place`
- **Info**: `info/current_stage` (평균값이 증가하는지 확인)
- **Gripper**: `info/gripper_movement` (그리퍼가 움직이는지 확인)

---

## V3 파일 구조

```
dofbot/source/dofbot/dofbot/tasks/direct/dofbot/
├── dofbot_pickplace_env_cfg_v3.py      # V3 환경 설정
├── dofbot_pickplace_env_v3.py          # V3 환경 구현
├── agents/
│   └── skrl_ppo_pickplace_v3_cfg.yaml  # V3 PPO 설정
└── __init__.py                          # V3 환경 등록
```
