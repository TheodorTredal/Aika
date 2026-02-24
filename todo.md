1. Top down approach, jeg er ikke så interesert i selve databehandling på edge nodene, for min del er det helt vilkårlig hvilken data som blir prosessert.
    Det er veldig enkelt å bli stuck i low-level detaljer hvis man begynner med Agentene. Det er egentlig ikke viktig når det kommer til selve arkitekturen
2. Jeg begynner med RAFT nodene
3. Deretter Local controller




For start av testingen:

1. Vi kan starte med 3 raft noder.
    Disse 3 raft nodene må kommunisere sammen, de må alle ha samme log som lederen, slik at de kjapt kan ta over om lederen feiler. Loggen kan piggybackes sammen med pings.
    Det skal ikke være mange raft noder 3-5 stk. Så Hver raft node kan lagre addressen til de andre nodene, man kan her bruke en dict for å lagre addressen til nodene og en True / False om noden er lederen for raft nodene.

    Leader will make decisions

    Leader can initially be selected based on its ID (Lowest number wins)

    vi trenger terms

    Vi må håndtere elections

    