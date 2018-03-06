const plan = require('flightplan');


plan.target('zero', {
    host: 'raspberrypi.local',
    username: 'pi',
    agent: process.env.SSH_AUTH_SOCK
}, {
    dir: 'opencv_tracking'
});


plan.local(function(local) {
    local.silent();
    local.log('uploading updates...');
    const filesToCopy = local.exec('git ls-files', {
        silent: true
    });
    local.transfer(filesToCopy, plan.runtime.options.dir);
});

plan.remote(function(remote) {

    remote["with"]("cd " + plan.runtime.options.dir, function () {
        // remote.log('installing dependencies...');
        // remote.exec('npm i');
        // remote.log('pruning dependencies...');
        // remote.exec('npm prune');
        // remote.log('reloading process...');
        // remote.exec('pm2 reload pm2.json --env development');
    });
});