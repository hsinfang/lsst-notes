```mermaid
gantt
    title Timeline
    dateFormat  YYYY-MM-DD HH:mm
    axisFormat  Day%d %H:%M

    Day 1 dayobs: 2026-01-01 12:00, 0h
    %% Dummy marker for observation start time
    twilight :obsstart, 2026-01-01 16:00, 0h
    observation :obs, 2026-01-01 16:00, 12h
    realtime procesing:2026-01-01 16:00, 12h
    embargo 80h :emb, after obs  , 80h
    unembargo :2026-01-05 00:00, 18h

    %%section Another
    Catchup resend missing raws: 2026-01-02 05:15, 1h
    Catchup autoingest: 2026-01-02 07:00, 1h
    Catchup processing:catchup, 2026-01-02 09:00, 3h
    unembargo :after emb, 6h

    DB sync: 3h
    buffer or other work: 15h
    Image publication : milestone, after

    APDB-PPDB replication:ppdb1, after catchup, 2h
    PPDB publication DIA tables & image md: milestone, after

    SSP processing: ssp, 2026-01-02 09:00, 4h
    MPC: mpc, after ssp, 4h
    SSP-PPDB ingest:ppdb2, after mpc, 2h
    PPDB publication SS tables: milestone, after
