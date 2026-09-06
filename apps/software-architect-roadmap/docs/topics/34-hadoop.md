# 34. Hadoop

[All 53 topics](../ROADMAP.md) · 6. Data and analytics · **Hadoop Streaming mapper and reducer**

## Meaning and purpose

Hadoop is an ecosystem that includes HDFS storage, YARN resource management, and MapReduce batch processing. MapReduce divides input, emits key-value pairs, shuffles records by key, and reduces each key group.

## How the example works

The mapper converts each JSON event to SKU and quantity separated by a tab. Sort performs the local shuffle. The reducer consumes a sorted stream and totals one SKU at a time. These scripts follow Hadoop Streaming stdin/stdout conventions and can run as actual Hadoop tasks.

Implementation: [examples/hadoop/mapper.py](../../examples/hadoop/mapper.py), [examples/hadoop/reducer.py](../../examples/hadoop/reducer.py), [data/events.jsonl](../../data/events.jsonl).

## Run and observe

Run from `apps/software-architect-roadmap`. See [setup and prerequisites](../../README.md) and [external integrations](../INTEGRATIONS.md).

```bash
python3 examples/hadoop/mapper.py < data/events.jsonl | sort | python3 examples/hadoop/reducer.py
```

Expected result: book has quantity 3 and pen has quantity 3. The integration guide includes the Hadoop jar invocation with -files, -mapper, -reducer, -input, and -output.

## Tradeoffs and failure cases

The local pipeline is not an HDFS/YARN cluster. Input must be sorted by key before reduction. A hot key can dominate one reducer, and whole-file sorting needs more memory or disk than the streaming reducer itself.

## Practice and interview discussion

Explain why the reducer uses bounded state while the shuffle may need external sorting. Add a combiner only after verifying the aggregation is safe to combine. Interview phrase: Map emits records, shuffle groups keys, and reduce aggregates each group.

Explain the requirement, the mechanism, and the failure boundary before naming a product. For an integrated interview answer, use [the order-system script](../SYSTEM_DESIGN.md).

## Reference

[Primary or official source](https://hadoop.apache.org/docs/stable/hadoop-streaming/HadoopStreaming.html). Checked on 2026-09-06. The implementation and exercises here are original educational examples; they are not copied from the linked source.
