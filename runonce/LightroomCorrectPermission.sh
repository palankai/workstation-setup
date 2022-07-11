#!/bin/bash
# reclaim Inactive memory due to memory leaks by Jenkins

echo === `date`

id=`id -u -nr`

home=/Users/$id

declare -a arr=( "Documents/Adobe/" "Library/Preferences/Adobe/" "Library/Caches/Adobe/" "Library/Application Support/Adobe/" )

for i in "${arr[@]}"
do
   echo "----------------------------------"
   echo "Process folder: $home/$i"

   echo "Restore owner: sudo chown -R $id $home/$i"
   sudo /usr/sbin/chown -R $id "$home/$i"

   echo "Restore read/write permission: chmod -RL +rwX $home/$i"
   /bin/chmod -RL +rwX "$home/$i"

   echo "Remove ACL: chmod -RN $home/$i"
   /bin/chmod -RN "$home/$i"
done
