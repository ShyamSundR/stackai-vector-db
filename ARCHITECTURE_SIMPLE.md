# StackAI Architecture - Quick Reference

## Simple Component Diagram

```ascii
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Layer                          │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────┤
│Libraries│Documents│ Chunks  │ Search  │ Health  │  Docs   │
│   API   │   API   │   API   │   API   │ Check   │ /docs   │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                           │
├─────────┬─────────┬─────────┬─────────┬─────────────────────┤
│Library  │Document │ Chunk   │Vector   │   Embedding         │
│Service  │Service  │Service  │Index    │   Service           │
│         │         │         │Service  │   (Cohere)          │
└─────────┴─────────┴─────────┴─────────┴─────────────────────┘
     │         │         │         │               │
     └─────────┼─────────┼─────────┘               │
               │         │                         │
               ▼         ▼                         ▼
┌──────────────────────────────────┐    ┌─────────────────────┐
│         Repository Layer        │    │     External API   │
├──────────────────────────────────┤    ├─────────────────────┤
│     LibraryRepository            │    │    Cohere API       │
│   ┌─────────────────────────┐    │    │  (Text→Embedding)   │
│   │ Thread-Safe Storage     │    │    └─────────────────────┘
│   │ (RLock Protected)       │    │
│   ├─────────────────────────┤    │
│   │ Libraries Dict[UUID]    │    │
│   │ Documents Dict[UUID]    │    │
│   │ Chunks Dict[UUID]       │    │
│   └─────────────────────────┘    │
└──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Vector Index Layer                          │
├─────────────────┬─────────────────┬─────────────────────────┤
│   BaseIndex     │ BruteForceIndex │    KDTreeIndex          │
│  (Abstract)     │    O(n) scan    │   O(log n) tree         │
│                 │   100% accuracy │   ~95% accuracy         │
└─────────────────┴─────────────────┴─────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Metadata Filtering                         │
├─────────────────────────────────────────────────────────────┤
│  MongoDB-style operators: $eq, $gt, $in, $contains, etc.   │
│  Nested field access: "author.name"                        │
│  Type-aware filtering: dates, numbers, strings, arrays     │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow (Simplified)

```ascii
Client Request
      │
      ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ FastAPI     │───▶│ Service     │───▶│ Repository  │
│ Router      │    │ Layer       │    │ (Thread     │
│ Validation  │    │ Business    │    │  Safe)      │
│ Serialization│   │ Logic       │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   │
                  ┌─────────────┐              │
                  │ Vector      │              │
                  │ Index       │              │
                  │ Search      │              │
                  └─────────────┘              │
                           │                   │
                           ▼                   │
                  ┌─────────────┐              │
                  │ Metadata    │              │
                  │ Filter      │              │
                  │ Apply       │              │
                  └─────────────┘              │
                           │                   │
                           └───────────────────┘
                                   │
                                   ▼
                              JSON Response
```

## Thread Safety Model

```ascii
┌─────────────────────────────────────────────────────────────┐
│                  Thread Safety Strategy                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Request 1 ──┐                                              │
│              │    ┌─────────────────┐                       │
│  Request 2 ──┼───▶│  RLock (Single) │──▶ Safe Operations    │
│              │    │  Repository     │                       │
│  Request 3 ──┘    │  Level Lock     │                       │
│                   └─────────────────┘                       │
│                                                             │
│     Pros: Simple, deadlock-free, adequate performance       │
│     Cons: Some contention under heavy concurrent load       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

##  Design Decisions & Trade-offs

```ascii


┌─────────────────────────────────────────────────────────────┐
│                    Concurrency Model Choice                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AsyncIO             vs.       Threading                    │
│  ├─ Complex async/await        ├─ Simple synchronous        │
│  ├─ NumPy incompatible         ├─ NumPy friendly            │
│  ├─ Whole-stack changes        ├─ Incremental adoption      │
│  └─ Over-engineering           └─ Adequate performance      │
│                                                             │
│  Actor Model      vs.       Shared State                    │
│  ├─ High complexity            ├─ Simple reasoning          │
│  ├─ Message overhead           ├─ Direct access             │
│  ├─ Overkill for scale         ├─ Fits current needs        │
│  └─ Learning curve             └─ Standard patterns         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

##  Performance Expectations

```ascii
┌─────────────────────────────────────────────────────────────┐
│                   Algorithm Performance                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Dataset Size │ BruteForce │  KDTree   │ Memory Usage       │
│  ─────────────┼────────────┼───────────┼──────────────      │
│  1K chunks    │    10ms    │    5ms    │     50MB           │
│  10K chunks   │   100ms    │   20ms    │    500MB           │
│  100K chunks  │     1s     │  100ms    │     5GB            │
│  1M chunks    │    10s     │  500ms    │    50GB            │
│                                                             │
│    BruteForce: Guaranteed optimal results                  │
│    KDTree: 5-10x faster, ~95% accuracy                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

##  Deployment Architecture

```ascii
┌─────────────────────────────────────────────────────────────┐
│                    Docker Deployment                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Docker Container                     │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │            FastAPI Application              │    │    │
│  │  │  ┌─────────────────────────────────────┐    │    │    │
│  │  │  │        Python Process              │    │    │    │
│  │  │  │  ┌─────────────────────────────┐    │    │    │    │
│  │  │  │  │    In-Memory Storage        │    │    │    │    │
│  │  │  │  │  (Thread-Safe Collections) │    │    │    │    │
│  │  │  │  └─────────────────────────────┘    │    │    │    │
│  │  │  └─────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                     │    │
│  │  Port: 8000                                         │    │
│  │  Health: /health                                    │    │
│  │  Docs: /docs                                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GitHub Push ──▶ Actions ──▶ Test ──▶ Build ──▶ Deploy     │
│                     │                                       │
│                     ├─ Unit Tests (pytest)                 │
│                     ├─ Integration Tests                    │
│                     ├─ Docker Build                        │
│                     ├─ Security Scan                       │
│                     └─ Performance Test                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

This architecture provides a **solid foundation** for a vector database while maintaining **simplicity** and **educational value**. The design allows for **natural evolution** as requirements grow! 
