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




RAFT NOTES
Election:
    - Når servere starter opp begynner alle som followers.
    - En node er i follower state så lenge den får gyldige kall fra lederen eller kandidaten.
    - Hvis en node ikke får kommunikasjon over en viss mengde tid så starter noden en ny election
        - Når en node begynner en election så inkrementerer den sin term og sender ut requestVote kall. En node gjør dette til en av tre ting skjer.
        a) Noden vinner election
        b) en annen server velger seg selv som lever
        c) en periode går uten at en node vinner.
    - en node vinner en election hvis den har majoriteten av stemmene
    - En node vil bare stemme på en kandidat per term.
    - Når en node har vunnet sender den ut heartbeats til alle andre noder og sier at jeg er den nye lederen.

    - Mens kandidat noden venter på stemmer, kan kandidat noden motta en AppendEntries RPC fra en annen server som sier at den er lederen. Hvis denne påståtte "lederen" sin term is like stor som kandidat noden sin term vil kandidat noden annerkjenne lederen som gyldig og returnere som følger, hvis RPC kallet er mindre enn kandidaten sitt term vil kandidaten ikke annerkjenne lederen og fortsette i kandidat modus.

    - Hvis det er ingen vinner så vil kandidat nodene få en timeout (random lengde her) og starte en ny election og inkrementere sin term count. Election timeouts are random (150-300ms) 

    Q:
    Er det sånn at en kandidat sender ut en ny term og spør om å bli leder, også svarer bare noden "ok jeg stemmer på deg". Hva hvis den noden som stemte fortsatt har kontakt med leder fra den forrige term?

    VIKTIG!!
        Lederen sender (pusher) heartbeats til alle sine følgere og følgerne responderer med 200 ok, dette må sjekkes litt dypere i, det har noe med append_entries å gjøre. 


    Lederen sender appendEntries (POST) kall til alle sine følgere, Når følgerene får en post request så timer de ikke ut.

    1. Begynn med selve leader election.
    2. Append entries.
