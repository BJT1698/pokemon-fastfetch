function fastfetch --description "Fastfetch with random Gen 2 (Crystal) animated Pokémon sprite and matching color theme"
    # If user provided logo arguments, delegate directly to standard fastfetch
    for arg in $argv
        if string match -q -- "--logo*" $arg; or string match -q -- "-l" $arg; or string match -q -- "--raw*" $arg
            command fastfetch $argv
            return
        end
    end

    set -l sprite_dir "$HOME/.local/share/pokemon-sprites/animated"
    if test -d "$sprite_dir"
        set -l sprites $sprite_dir/*.raw
        if test (count $sprites) -gt 0
            set -l chosen_sprite (random choice $sprites)
            set -l base (string replace -r '\.raw$' '' (path basename $chosen_sprite))
            set -l parts (string split "_" $base)
            set -l num $parts[1]
            set -l name $parts[2]
            set -l p_col "#"$parts[3]
            set -l s_col "#"$parts[4]
            
            # Capitalize hyphenated names properly (e.g. ho-oh -> Ho-Oh, mr-mime -> Mr-Mime)
            set -l cap_name (string join "-" (for seg in (string split "-" $name); echo (string upper (string sub -l 1 $seg))(string sub -s 2 $seg); end))
            set -gx POKEMON_NAME "$cap_name (#$num)"
            
            command fastfetch \
                --raw "$chosen_sprite" \
                --color-keys "$p_col" \
                --color-title "$p_col" \
                --color-separator "$s_col" \
                --logo-width 22 \
                --logo-height 11 \
                --logo-padding-right 3 \
                $argv
            return
        end
    end

    command fastfetch $argv
end
