#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int main() {
  pid_t pid = fork();

  if (pid < 0) {
    return 1;
  }

  if (pid > 0) {
    // Parent process exits immediately, satisfying the OS that the 'App' has
    // launched
    return 0;
  }

  // Child process continues in background
  // Create a new session to detach from controlling terminal
  setsid();

  // Redirect standard files to a log file for debugging (silent to user)
  int log_fd = open("/tmp/tma_launch.log", O_RDWR | O_CREAT | O_TRUNC, 0666);
  if (log_fd > 0) {
    dup2(log_fd, STDOUT_FILENO);
    dup2(log_fd, STDERR_FILENO);
    close(log_fd);
  }

  // Execute the shell script
  execl("/bin/bash", "bash", "/Users/john/Projects/test/TMA Project/run_tma.sh",
        NULL);

  return 0;
}
