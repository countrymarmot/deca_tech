(function(){
    var job_template = _.template($("#job-template").html());

    var fetch_min = -1;
    var jobs = {};

    var updateJobHTML = function(tag, job) {
        tag.html(job_template({job: job}));
        var collapsed = tag.hasClass('collapsed');
        tag.removeClass();
        if (collapsed) {
            tag.addClass('collapsed');
        }
        if (job.status === "RUNNING") {
            tag.removeClass('collapsed');
        }
        tag.addClass(job.status.toLowerCase());
        tag.find("job-header").disableSelection();
        tag.find("job-header").click(function() {
            $(this).parent().toggleClass("collapsed");
        });
    };

    var updateJobs = function(data) {
        fetched_jobs = $.parseJSON(data);
        $.each(fetched_jobs, function(i, job) {
            if (job.id in jobs) {
                if (!(job.status === "COMPLETE" && jobs[job.id].status === "COMPLETE")) {
                    updateJobHTML($("#job" + job.id), job);
                    jobs[job.id] = job;
                }
            } else {
                var job_element = $("<job></job>").html(job_template({job: job}));
                if (job.status !== "RUNNING") {
                    job_element.addClass("collapsed");
                }
                job_element.addClass(job.status.toLowerCase());
                job_element.find("job-header").disableSelection();
                job_element.find("job-header").click(function() {
                    $(this).parent().toggleClass("collapsed");
                });
                job_element.attr("id", "job" + job.id);
                $("#job-list").prepend(job_element);
                console.log(job);
                jobs[job.id] = job;
            }
        });
    };

    var fetchNewJobs = function() {
        $.ajax({
            url: ('/opal/api/jobs/' + fetch_min),
            success: updateJobs
        });
    };

    $(document).ready(function() {
        window.setInterval(fetchNewJobs, 1000);
        fetchNewJobs();
    });
})();
