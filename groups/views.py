from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Group, Post, GROUP_TAG, POST_TAG
from django.contrib.auth.models import User


from mainPage.function import getTableSlot, getTable, getDayNumber
from mainPage.models import Activity

from user.models import UserInfo


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

    groups = Group.objects.filter(gmembers=request.user).order_by('gname')
    return render(request, 'groups/group.html', {'groups': groups, 'GROUP_TAG': GROUP_TAG})


def group_schedule(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # join activities of all group member together
    group_activities = Activity.objects.none()
    for member in group.gmembers.all():
        activity = Activity.objects.filter(user=member)
        group_activities = group_activities | activity
    # make timeslots out of activities
    table_slot = getTableSlot(group_activities)
    table = getTable(table_slot)
    timeRange = [str(hour) + ":00" for hour in range(24)]
    return render(request, 'groups/group_schedule.html', {'group': group,
                                                          'timeRange': timeRange,
                                                          'table': table,
                                                          }
                  )

def group_schedule_by_day(request, group_id, day_name):
    timeRange = [str(hour) + ":00" for hour in range(24)]
    day_number = getDayNumber(day_name)

    #get group from id
    group = get_object_or_404(Group, id=group_id)
    group_activities = Activity.objects.none()
    
    table = []
    #make list of all members
    members = group.gmembers.all();
    for member in members:
        #add username to the first col of each row in table
        row = [member.username]

        #get table slot from activity
        activity = Activity.objects.filter(user=member)
        table_slot = getTableSlot(activity)

        #only append the chosen day's table slot into row
        chosen_slot = table_slot[day_number]
        for slot in chosen_slot:
            row.append(slot)

        table.append(row)
    return render(request, 'groups/group_schedule_by_day.html', {'group': group,
                                                        'timeRange': timeRange,
                                                        'day_name': day_name,
                                                        'table': table,
                                                        }
                                                        )

def group_members(request, group_id):
    user = User.objects.get(username=request.user.username)
    user_info = UserInfo.objects.get(user_id=user)

    group = get_object_or_404(Group, id=group_id)
    members = group.gmembers.all()

    return render(request, 'groups/group_members.html', {'group': group, 'members': members, 'user_info': user_info})


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


def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if not group.is_creator(request.user):
        return HttpResponseForbidden("You are not the creator of this group.")

    if request.method == 'POST':
        gname = request.POST['gname']
        gdescription = request.POST['gdescription']
        gtag = request.POST['gtag']
        gprofile = request.FILES.get('gprofile')

        if not gname or not gdescription:
            messages.error(request, "Group name and description are required.")
            return render(request, 'groups/edit_group.html', {'group': group, 'GROUP_TAG': GROUP_TAG})

        group.gname = gname
        group.gdescription = gdescription
        group.gtag = gtag
        group.gprofile = gprofile
        group.save()

        messages.success(
            request, "Group details have been updated successfully.")
        return redirect('group')

    return render(request, 'groups/edit_group.html', {'group': group, 'GROUP_TAG': GROUP_TAG})


def post(request, group_id):
    user = User.objects.get(username=request.user.username)
    user_info = UserInfo.objects.get(user_id=user)

    tag_filter = request.GET.get('ptag', '')

    group = get_object_or_404(Group, id=group_id)
    posts = Post.objects.filter(
        pgroup_id=group_id, ptag__icontains=tag_filter).order_by('-pcreated_on')
    return render(request, 'groups/post.html', {'posts': posts, 'POST_TAG': POST_TAG, 'group': group, 'user_info' : user_info})


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


def edit_post(request, group_id, post_id):
    group = get_object_or_404(Group, id=group_id)
    post = get_object_or_404(Post, id=post_id)

    if not post.pauthor == request.user:
        return HttpResponseForbidden("You are not the author of this post.")

    if request.method == 'POST':
        ptitle = request.POST.get('ptitle', '')
        pcontent = request.POST.get('pcontent', '')
        ptag = request.POST.get('ptag', '')

        if not ptitle or not pcontent or not ptag:
            messages.error(request, "All fields are required.")
            return render(request, 'groups/edit_post.html', {'group': group, 'post': post, 'POST_TAG': POST_TAG})

        post.ptitle = ptitle
        post.pcontent = pcontent
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


# def remove_member(request, group_id):
#    group = get_object_or_404(Group, id=group_id)
#    gmembers = group.gmembers.all()
#    if request.method == 'POST':
#        selected_members = request.POST.getlist('selected_members')
#
#        for member_id in selected_members:
#            try:
#                user = User.objects.get(id=member_id)
#                group.gmembers.remove(user)
#            except User.DoesNotExist:
#                pass
#
#        messages.success(request, "Selected members have been removed.")
#        return redirect('group_members', group_id=group_id)
#
#    return render(request, 'groups/remove_member.html', {'group': group})

def remove_member(request, group_id):
    user = User.objects.get(username=request.user.username)
    user_info = UserInfo.objects.get(user_id=user)

    group = get_object_or_404(Group, id=group_id)
    members = group.gmembers.all()

    if request.method == 'POST':
        selected_members = request.POST.getlist('selected_members')

        for member_id in selected_members:
            member_to_remove = get_object_or_404(User, id=member_id)
            group.gmembers.remove(member_to_remove)
            messages.success(request, "Selected members have been removed.")

        return render(request, 'groups/remove_member.html', {'group': group, 'members': members})

    return render(request, 'groups/remove_member.html', {'group': group, 'members': members, 'user_info': user_info})


@login_required
def add_member(request, group_id):

    group = get_object_or_404(Group, id=group_id)
    gmembers = group.gmembers.all()
    if request.method == 'POST':
        account_UID = request.POST.get(
            'account_UID')

        try:
            user_info = UserInfo.objects.get(account_UID=account_UID)
            user = User.objects.get(username=user_info.user_id)
            group.gmembers.add(user)
        except User.DoesNotExist:
            messages.error(
                request, f"User with ID {account_UID} does not exist.")
            return render(request, 'groups/add_member.html', {'group_id': group_id, 'group': group})

        messages.success(
            request, f"User {user.username} has been added to the group.")
        return redirect('group_members', group_id=group_id)

    return render(request, 'groups/add_member.html', {'group_id': group_id, 'group': group})
