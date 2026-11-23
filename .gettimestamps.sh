#!/bin/sh

# Use UTC when reading and formatting file timestamps.
export TZ=UTC0

case `uname -s` in
    "Linux" )
        MYDATEFORTOUCH() {
            date -d"$(stat -c %y "$1")" +%Y%m%d%H%M.%S
        }
        ;;
    "Darwin" )
        MYDATEFORTOUCH() {
            /usr/bin/stat -f %Sm -t %Y%m%d%H%M.%S "$1"
        }
        ;;
    * )
        MYDATEFORTOUCH() {
            echo 197001010000.00
        }
        ;;
esac

# Use UTC also when restoring the saved timestamps.
{
    echo '#!/bin/sh'
    echo 'export TZ=UTC0'
} > .resettimestamps.sh

IFS='
'

for file in `git ls-files`
do
    [ "$file" != ".resettimestamps.sh" ] && \
	echo "touch -ch -t $(MYDATEFORTOUCH "$file") \"$file\"" >> .resettimestamps.sh
done

chmod u+x .resettimestamps.sh
