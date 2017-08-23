#!/bin/bash

USERNAME=cloner
GROUP=cloner

groupadd $GROUP
useradd -g $GROUP -M $USERNAME
usermod -L $USERNAME
