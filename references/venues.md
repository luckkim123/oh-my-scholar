# Venue Configuration Card

> 학회/저널별 제약 SSOT. scholar-outline(섹션·페이지)·scholar-verify(page_limit·인용수)·scholar-drafter(class·template)가 참조. paper-write venues YAML을 단순화해 흡수.

## 스키마

```yaml
name:            # 표시명 (IROS 2026)
key:             # 식별자 (iros)
class:           # \documentclass (ieeeconf)
compile_engine:  # pdflatex | xelatex | lualatex
bib_style:       # IEEEtran
page_limit:      # 정수 또는 null(무제한)
sections:        # [Introduction, Related Work, Method, ...]
required_sections: # 필수 섹션
quality_threshold: # verify 통과 점수 (0-100, 기본 80)
max_review_rounds: # revise 루프 최대 (기본 5)
regression_threshold: # 점수 하락 허용치 (기본 5)
min_citations:   # 최소 인용 수
self_citation_max_ratio: # 자기인용 상한 (기본 0.20)
review_weights:  # {logic: 1.0, prose: 0.8, ...} inspect 가중

# ── ⭐ self-specialization 메타 (H5 — heavy-channel backport, 2026-05-31) ──
specificity:     # 0..1 — 이 venue 기본값 중 *학습으로 굳은* 비율 (0=순수 템플릿 default, 1=완전 사용자 특화)
                 #   = (origin∈{inductive,learned} 항목 수) / (활성 기본값 항목 수). monotonic(승격은 올리거나 유지).
                 #   계산·갱신 규칙은 references/learning-protocol.md §4가 SSOT.
origins:         # 항목별 출처 맵 {required_sections: learned, section_order: preset, ...}
                 #   preset=템플릿 default(0.0) / inductive=과거 논문서 도출(1.0) / learned=learned.md 승격(1.0)
learned_refs:    # [OBS-0003, ...] — learned 기본값의 provenance (어느 관찰서 승격됐나). silent 변경 금지(§6.C).
```

> ⚠️ **이 세 필드는 `scholar-learn`(사람 게이트 통과 후)만 쓴다.** 사용자가 직접 venue 값을 적을 땐
> 안 써도 됨(미지정 = 전부 preset = specificity 0). 자동 강제 금지: confidence·evidence 아무리
> 높아도 사람 승인 없이 venue 기본값 안 바뀜(`learning-protocol.md` §6.B). citation/.bib 류는
> 영구히 이 메타의 승격 대상 아님(§6.F).

## 예시 — IROS (conference)

```yaml
name: "IROS 2026"
key: iros
class: ieeeconf
compile_engine: pdflatex
bib_style: IEEEtran
page_limit: 6
sections: [Introduction, Related Work, Method, Experiments, Conclusion]
quality_threshold: 80
max_review_rounds: 5
min_citations: 15
self_citation_max_ratio: 0.20
review_weights: {logic: 1.0, prose: 0.8}
```

## 예시 — POSTECH 석사논문 (thesis)

```yaml
name: "POSTECH M.Sc. Thesis"
key: postech_msc_thesis
class: report
compile_engine: xelatex   # 한글 포함
page_limit: null
quality_threshold: 80
min_citations: 50
review_weights: {logic: 1.2, prose: 1.2}
```

## 예시 — 학습으로 특화된 IROS (specificity > 0)

`scholar-learn`이 "IROS는 항상 Ablation 포함"을 사람 게이트 통과로 승격한 뒤의 모습:

```yaml
name: "IROS 2026"
key: iros
required_sections: [Introduction, Related Work, Method, Experiments, Ablation, Conclusion]
self_citation_max_ratio: 0.10        # 사용자 습관 "self-cite 0.1 밑" 승격됨
# ── 메타 ──
specificity: 0.29                    # 7개 활성 기본값 중 2개(Ablation, self-cite)가 learned → 2/7 = 0.29
# origins 는 7개 활성 기본값 전부 나열 (분모 = 7, 분자 = learned 2개) — 분수와 1:1 일치해야 함(§4)
origins: {required_sections: learned, self_citation_max_ratio: learned, sections: preset, page_limit: preset, quality_threshold: preset, max_review_rounds: preset, min_citations: preset}
learned_refs: [OBS-0003, OBS-0011]   # provenance: 어느 관찰서 왔나
```

## 참고

- venue 파일은 `.oms/venues/<key>.yaml` 또는 사용자 프로젝트에 둠. oms는 이 카드를 스키마 SSOT로 삼고, 실제 값은 프로젝트별.
- `template_dir` 류 절대경로 결합은 두지 않음 (paper-write 결합점 ①④ 회피). venue는 선언적 제약만.
- ⭐ **self-specialization**: `specificity`·`origins`·`learned_refs`는 "쓸수록 이 사용자에게 특화"의 디스크 흔적. 동역학은 `references/learning-protocol.md`(2채널·승격 기준·specificity 공식)가 SSOT. heavy 채널 승격은 항상 사람 게이트.
