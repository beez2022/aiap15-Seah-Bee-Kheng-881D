while getopts c:d: flag
do
    case "${flag}" in 
        c) config_file=${OPTARG};;
        d) db_path=${OPTARG};;
    esac
done

python src/run_algo.py -c $config_file -d $db_path
