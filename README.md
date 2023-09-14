# TrackProject_MinhyeokKim

## Start up

```bash
git clone https://github.com/likelion-backend-6th/TrackProject_1_MinhyeokKim.git sns_app
```

```bash
cd sns_app
docker-compose up --build -d
```

Dummy data creation at first

```bash
python manage.py create_dummy_data
```

## Project Concept

- "트위터" 와 같은 소셜 네트워크 서비스 애플리케이션 개발
- 백엔드 API: Django REST Framework
- CICD: Github actions
- Cloud: Naver Cloud Platform
- Terraform 을 이용하여 IaC 구현
- k8s 로 오케스트레이션 구현

## Development Checklist

### 1. 백엔드 DB 설계

- [x] Post
- [x] Follow

#### DB modeling

##### Post

| Model | Field Name   | Data Type     | Description   | Relationship                            |
| ----- | ------------ | ------------- | ------------- | --------------------------------------- |
| Post  | user         | ForeignKey    | Post creator  | Linked to User model, CASCADE on delete |
| Post  | content      | TextField     | Post content  | None                                    |
| Post  | created_date | DateTimeField | Creation date | Automatically set                       |
| Post  | updated_date | DateTimeField | Update date   | Automatically set                       |

##### Follow

| Model  | Field Name | Data Type  | Description | Relationship                            |
| ------ | ---------- | ---------- | ----------- | --------------------------------------- |
| Follow | follower   | ForeignKey | Follower    | Linked to User model, CASCADE on delete |
| Follow | following  | ForeignKey | Following   | Linked to User model, CASCADE on delete |

### 2. 백엔드 API 개발

- 유저
  - [x] 사용자 본인을 제외한 전체 사용자 목록을 확인할 수 있다.
  - [ ] 전체 유저 목록을 불러올 때, 사용자가 해당 유저를 follow하고 있는지 여부를 알 수 있다.
- 게시글
  - [x] 사용자는 모든 게시글을 볼 수 있다.
  - [x] 사용자는 게시글을 올릴 수 있다.
  - [x] 사용자는 본인의 게시물을 모아볼 수 있다.
  - [x] 사용자는 본인의 게시물을 수정하거나, 삭제할 수 있다.
  - [x] 사용자는 본인의 게시물을 숨김(숨김해제)처리할 수 있다.
  - [x] 숨김처리된 게시물은 사용자 본인만 볼 수 있고, 다른 사용자는 볼 수 없다.
  - [ ] 게시물에 사진을 추가할 수 있다.
- follow
  - [x] 사용자는 다른 사용자를 follow(unfollow)할 수 있다.
  - [x] 사용자는 follow한 사람들 목록을 확인할 수 있다.
  - [x] 사용자는 나를 follow하고 있는 사람들 목록을 확인할 수 있다.
  - [x] 사용자는 follow한 사람들이 올린 게시물을 모아볼 수 있다.

### 3. 더미데이터 추가

- [x] 사용자 5명 이상
- [x] 사용자당 게시글 3개 이상

### 4. 테스트 코드 작성

- [x] 전체 사용자 목록에서 자신을 제외한 목록이 잘 나오는지 테스트
- [x] 모든 게시물이 출력되는지 테스트
- [x] 본인의 게시물만 수정, 삭제가 가능한지 테스트
- [x] follow / unfollow 기능이 잘 작동하는지 테스트
- [x] follow한 사람들이 올린 게시물을 잘 확인할 수 있는지 테스트

### 5. 배포

- [x] runserver, gunicorn 등을 사용해서 배포
- [x] 어디서든 API 호출이 가능하도록 백엔드 서버를 클라우드 서비스를 통해 배포

### 6. CICD Pipeline 작성

- [x] Github actions로 구현
- [x] push가 됐을 때, 테스트 코드를 실행하여, 테스트가 정상 작동하는지 확인하고, 정상 작동하면, 서버에 새 버전을 배포

### 7. terraform 작성

- [ ] 배포 및 운영에 필요한 모든 인프라를 terraform으로 관리한다.

### 8. multi-stage 구성

- [ ] production과 staging 환경을 별도로 구성한다.
- [ ] terraform 으로 손쉽게 각 환경을 구성(apply)하고, 폐기(destroy)할 수 있다.

### 9. k8s로 배포

- [ ] 서비스를 k8s로 배포한다.

### 10. 백엔드 서버 분리

- [x] 백엔드 서버와 DB 서버를 물리적으로 분리

## Challenging Task

### 도커 컨테이너로 배포

- [x] docker image를 이용한 container로 배포

### 로드밸런서를 통해 배포

- [x] 인스턴스에 직접 접근하는 대신 로드밸런서를 통해 API를 호출할 수 있도록 배포
  > http://sns-lb-staging-19447035-3f19227be0e5.kr.lb.naverncp.com/sns/post/

### CICD Pipeline 작성

- [x] PR이 있을 때, 테스트 코드를 실행하여, 테스트가 정상 작동하는지 확인

### monitoring 시스템 구축

- [ ] 500에러 혹은 scale up/down이 일어날 때, 알람을 보낸다.

### terraform modulizing

- [ ] terraform 코드를 모듈화하여 재사용 가능하게 만든다.

### K8s CICD 구축

- [ ] k8s CICD 파이프라인을 구축한다.

### 주요 설치 패키지/모듈

|          이름           |  버전  |
| :---------------------: | :----: |
|       **python**        | 3.11.4 |
|       **Django**        | 4.2.5  |
|     **PostgreSQL**      |   13   |
|  **PostgreSQL local**   |   15   |
|      **gunicorn**       | 21.2.0 |
|   **psycopg2-binary**   | 2.9.7  |
| **djangorestframework** | 3.14.0 |
|     **django-seed**     | 0.3.1  |
|   **drf-spectacular**   | 0.26.4 |
