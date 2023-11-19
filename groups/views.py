from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Group, Post, GROUP_TAG, POST_TAG

from mainPage.function import getTableSlot
from mainPage.models import Activity


@login_required
def create_group(request):
    if request.method == 'POST':
        gname = request.POST['gname']
        gdescription = request.POST['gdescription']
        gtag = request.POST['gtag']
        gprofile = request.FILES.get('gprofile')

        if gname and gdescription:
            new_group = Group.objects.create(
                gname=gname,
                gdescription=gdescription,
                gtag=gtag,
                gprofile=gprofile,
                gcreator=request.user)
            new_group.gmembers.add(request.user)

            return redirect('group')
    return render(request, 'groups/create_group.html', {'GROUP_TAG': GROUP_TAG})


def group_schedule(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # join activities of all group member together
    group_activities = Activity.objects.none()
    for member in group.gmembers.all():
        activity = Activity.objects.filter(user=member)
        group_activities = group_activities | activity
    # make timeslots out of activities
    table_slot = getTableSlot(group_activities)
    timeRange = [str(hour) + ":00" for hour in range(24)]
    return render(request, 'groups/group_schedule.html', {'group': group, 
        'timeRange': timeRange,
        'slot_sunday': table_slot[0],
        'slot_monday': table_slot[1],
        'slot_tuesday': table_slot[2],
        'slot_wednesday': table_slot[3],
        'slot_thursday': table_slot[4],
        'slot_friday': table_slot[5],
        'slot_saturday': table_slot[6],
    }
    )


def group_members(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.gmembers.all()

    return render(request, 'groups/group_members.html', {'group': group, 'members': members})


def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        if request.user in group.gmembers.all():
            group.gmembers.remove(request.user)
            messages.success(request, "You have left the group.")
            return redirect('group')
        else:
            return HttpResponseForbidden("You are not a member of this group.")

    return HttpResponseForbidden("Invalid request.")


@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if not group.is_creator(request.user):
        return HttpResponseForbidden("You are not the creator of this group.")

    if request.method == 'POST':
        gname = request.POST['gname']
        gdescription = request.POST['gdescription']
        gtag = request.POST['gtag']
        gprofile = request.FILES.get('gprofile')

        if gname:
            group.gname = gname
        if gdescription:
            group.gdescription = gdescription
        if gtag:
            group.gtag = gtag
        if gprofile:
            group.gprofile = gprofile

        group.save()

        messages.success(
            request, "Group details have been updated successfully.")
        return redirect('group')

    return render(request, 'groups/edit_group.html', {'group': group, 'GROUP_TAG': GROUP_TAG})


def post(request, group_id):
    tag_filter = request.GET.get('ptag', '')

    group = get_object_or_404(Group, id=group_id)
    posts = Post.objects.filter(
        pgroup_id=group_id, ptag__icontains=tag_filter).order_by('-pcreated_on')
    return render(request, 'groups/post.html', {'posts': posts, 'POST_TAG': POST_TAG, 'group': group})


def create_post(request, group_id):
    if request.method == 'POST':
        ptitle = request.POST['ptitle']
        pcontent = request.POST['pcontent']
        ptag = request.POST['ptag']
        group = get_object_or_404(Group, id=group_id)

        if ptitle and pcontent:
            Post.objects.create(
                ptitle=ptitle,
                pcontent=pcontent,
                ptag=ptag,
                pauthor=request.user,
                pgroup=group
            )
            return redirect('post', group_id=group.id)
    return render(request, 'groups/create_post.html', {'POST_TAG': POST_TAG, 'group': group})


@login_required
def edit_post(request, group_id, post_id):
    group = get_object_or_404(Group, id=group_id)
    post = get_object_or_404(Post, id=post_id)

    if not post.pauthor == request.user:
        return HttpResponseForbidden("You are not the author of this post.")

    if request.method == 'POST':
        ptitle = request.POST.get('ptitle', '')
        pcontent = request.POST.get('pcontent', '')
        ptag = request.POST.get('ptag', '')

        if ptitle:
            post.ptitle = ptitle
        if pcontent:
            post.pcontent = pcontent
        if ptag:
            post.ptag = ptag

        post.save()

        messages.success(request, "Post has been updated successfully.")
        return redirect('post', group_id=group_id)

    return render(request, 'groups/edit_post.html', {'group': group, 'post': post,  'POST_TAG': POST_TAG})


def delete_post(request, group_id):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        if request.user != post.pauthor or group_id != post.pgroup_id:
            messages.error(
                request, "You don't have permission to delete this post.")
        else:
            post.delete()
            messages.success(request, "Post deleted successfully.")

    return redirect('post', group_id=group_id)
