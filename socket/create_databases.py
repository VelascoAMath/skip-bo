from configparser import ConfigParser

import psycopg2

parser = ConfigParser()
parser.read('database.ini')
config = dict(parser.items('postgresql'))

with psycopg2.connect(**config) as conn:
    cur = conn.cursor()
    cur.execute(
        """
CREATE TABLE IF NOT EXISTS public.user (
    id uuid NOT NULL,
    name text NOT NULL,
    token text NOT NULL,
    CONSTRAINT user_pk PRIMARY KEY (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS user_name_idx ON public.user USING btree (name);

CREATE TABLE IF NOT EXISTS public.game (
    id uuid NOT NULL,
    deck json NOT NULL,
    "discard" json NOT NULL,
    current_user_id uuid NOT NULL,
    "owner" uuid NOT NULL,
    in_progress bool DEFAULT false NOT NULL,
    winner uuid NULL,
    CONSTRAINT game_pk PRIMARY KEY (id),
    CONSTRAINT game_user_current_fk FOREIGN KEY (current_user_id) REFERENCES public."user"(id) ON DELETE CASCADE,
    CONSTRAINT game_user_owner_fk FOREIGN KEY ("owner") REFERENCES public."user"(id) ON DELETE CASCADE,
    CONSTRAINT game_user_winner_fk FOREIGN KEY (winner) REFERENCES public."user"(id)
);




CREATE TABLE IF NOT EXISTS public.player (
    id uuid NOT NULL,
    game_id uuid NOT NULL,
    user_id uuid NOT NULL,
    hand json NOT NULL,
    stock json NOT NULL,
    turn_index serial NOT NULL,
    took_action boolean DEFAULT false NOT NULL,
    did_discard bool DEFAULT false NOT NULL,
    CONSTRAINT player_pk PRIMARY KEY (id),
    CONSTRAINT player_game_fk FOREIGN KEY (game_id) REFERENCES public.game(id) ON DELETE CASCADE,
    CONSTRAINT player_user_fk FOREIGN KEY (user_ud) REFERENCES public."user"(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS player_game_id_idx ON public.player (game_id,user_ud);
CREATE UNIQUE INDEX IF NOT EXISTS player_turn_index_idx ON public.player (turn_index,game_id);
CREATE INDEX IF NOT EXISTS player_game_id_idx ON public.player (game_id);
CREATE INDEX IF NOT EXISTS player_user_ud_idx ON public.player (user_ud);




CREATE TABLE IF NOT EXISTS public.gamebuild (
    id uuid NOT NULL,
    game_id uuid NOT NULL,
    deck json NOT NULL,
    sort_key serial NOT NULL,
    CONSTRAINT gamebuild_pk PRIMARY KEY (id),
    CONSTRAINT gamebuild_game_fk FOREIGN KEY (game_id) REFERENCES public.game(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS gamebuild_sort_key_idx ON public.gamebuild (sort_key);

CREATE TABLE IF NOT EXISTS public.playerdiscard (
    id uuid NOT NULL,
    player_id uuid NOT NULL,
    deck json NOT NULL,
    sort_key serial NOT NULL,
    CONSTRAINT playerdiscard_pk PRIMARY KEY (id),
    CONSTRAINT playerdiscard_player_fk FOREIGN KEY (player_id) REFERENCES public.player(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS playerdiscard_sort_key_idx ON public.playerdiscard (sort_key);

        """)
