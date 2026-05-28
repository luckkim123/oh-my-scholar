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
```

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

## 참고

- venue 파일은 `.oms/venues/<key>.yaml` 또는 사용자 프로젝트에 둠. oms는 이 카드를 스키마 SSOT로 삼고, 실제 값은 프로젝트별.
- `template_dir` 류 절대경로 결합은 두지 않음 (paper-write 결합점 ①④ 회피). venue는 선언적 제약만.
